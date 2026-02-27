"""Entry point for the PostgreSQL Azure Backup service."""

import sys
from postgres_azure_backup.backup_service import run_backup_job


def main() -> None:
    """Main entry point."""
    try:
        run_backup_job()
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
