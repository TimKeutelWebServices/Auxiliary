"""PostgreSQL backup service with Azure Storage integration."""

import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from azure.storage.blob import BlobClient, StandardBlobTier
from dotenv import load_dotenv

# Configure logging - only errors and key metrics
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create info logger for key metrics only
info_logger = logging.getLogger(f"{__name__}.metrics")
info_handler = logging.StreamHandler()
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
info_logger.addHandler(info_handler)
info_logger.setLevel(logging.INFO)
info_logger.propagate = False


def load_environment() -> dict:
    """Load environment variables from .env file and environment."""
    load_dotenv()
    
    required_vars = [
        'DATABASE_HOST',
        'DATABASE_PORT',
        'DATABASE_NAME',
        'DATABASE_USERNAME',
        'DATABASE_PASSWORD',
        'AZURE_STORAGE_CONNECTION_STRING',
    ]
    
    config = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        config[var] = value
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return config


def create_backup(
    database_host: str,
    database_port: str,
    database_name: str,
    database_username: str,
    database_password: str,
    backup_dir: Optional[str] = None
) -> Path:
    """Create a PostgreSQL backup using pg_dump.
    
    Args:
        database_host: PostgreSQL host
        database_port: PostgreSQL port
        database_name: Database name
        database_username: Database username
        database_password: Database password
        backup_dir: Directory to store the backup
        
    Returns:
        Path to the backup file
        
    Raises:
        RuntimeError: If backup creation fails
    """
    if backup_dir is None:
        backup_dir = tempfile.gettempdir()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{database_name}_{timestamp}.sql"
    backup_path = Path(backup_dir) / backup_filename
    
    info_logger.info(f"Backup started: {backup_filename}")
    start_time = time.time()
    
    env = os.environ.copy()
    env['PGPASSWORD'] = database_password
    
    try:
        cmd = [
            'pg_dump',
            '-h', database_host,
            '-p', database_port,
            '-U', database_username,
            '-d', database_name,
            '-F', 'plain',
        ]
        
        with open(backup_path, 'w') as f:
            subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                check=True,
                text=True,
                timeout=3600
            )
        
        elapsed_time = time.time() - start_time
        file_size_mb = backup_path.stat().st_size / (1024*1024)
        info_logger.info(f"Backup completed: {backup_filename} ({file_size_mb:.2f}MB, {elapsed_time:.2f}s)")
        
        return backup_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"pg_dump failed: {e.stderr}")
        if backup_path.exists():
            backup_path.unlink()
        raise RuntimeError(f"Backup creation failed: {e.stderr}") from e
    except FileNotFoundError:
        logger.error("pg_dump not found - PostgreSQL client tools not installed")
        raise RuntimeError("pg_dump command not found") from None
    except subprocess.TimeoutExpired:
        logger.error("Backup timed out after 1 hour")
        if backup_path.exists():
            backup_path.unlink()
        raise RuntimeError("Backup creation timed out") from None
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        if backup_path.exists():
            backup_path.unlink()
        raise


def upload_to_azure(
    backup_path: Path,
    connection_string: str,
    container_name: str = "backups"
) -> Optional[str]:
    """Upload backup file to Azure Blob Storage.
    
    Args:
        backup_path: Path to the backup file
        connection_string: Azure Storage connection string
        container_name: Name of the blob container
        
    Returns:
        Name of the uploaded blob
        
    Raises:
        RuntimeError: If upload fails
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    blob_name = backup_path.name
    file_size = backup_path.stat().st_size
    
    info_logger.info(f"Upload started: {blob_name}")
    start_time = time.time()
    
    try:
        with open(backup_path, 'rb') as data:
            blob_client = BlobClient.from_connection_string(
                connection_string,
                container_name=container_name,
                blob_name=blob_name
            )
            
            blob_client.upload_blob(data, overwrite=True)
            blob_client.set_standard_blob_tier(StandardBlobTier.ARCHIVE)
            
            elapsed_time = time.time() - start_time
            info_logger.info(
                f"Upload completed: {blob_name} ({file_size / (1024*1024):.2f}MB, {elapsed_time:.2f}s)"
            )
            
            return blob_name
            
    except Exception as e:
        logger.error(f"Upload to Azure failed: {e}")
        raise RuntimeError(f"Upload to Azure failed: {e}") from e


def cleanup_local_backup(backup_path: Path) -> None:
    """Delete the local backup file.
    
    Args:
        backup_path: Path to the backup file
    """
    try:
        if backup_path.exists():
            backup_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to delete local backup: {e}")


def run_backup_job() -> None:
    """Execute the complete backup workflow."""
    job_start = time.time()
    info_logger.info("Backup job started")
    
    try:
        # Load configuration
        config = load_environment()
        
        # Create backup
        backup_path = create_backup(
            database_host=config['DATABASE_HOST'],
            database_port=config['DATABASE_PORT'],
            database_name=config['DATABASE_NAME'],
            database_username=config['DATABASE_USERNAME'],
            database_password=config['DATABASE_PASSWORD'],
        )
        
        # Upload to Azure
        blob_name = upload_to_azure(
            backup_path=backup_path,
            connection_string=config['AZURE_STORAGE_CONNECTION_STRING'],
        )
        
        # Cleanup local backup
        cleanup_local_backup(backup_path)
        
        total_time = time.time() - job_start
        info_logger.info(f"Backup job completed successfully (total: {total_time:.2f}s)")
        
    except Exception as e:
        total_time = time.time() - job_start
        logger.error(f"Backup job failed after {total_time:.2f}s: {e}")
        raise


if __name__ == "__main__":
    run_backup_job()
