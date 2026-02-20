#!/usr/bin/env python
import json
import sys
from pathlib import Path


# Define schemas based on the normalized data structure
REVIEW_SCHEMA = {
    "kind": "collectionType",
    "collectionName": "reviews",
    "info": {
        "singularName": "review",
        "pluralName": "reviews",
        "displayName": "Google Business Review",
        "description": "Reviews from Google Business Profile",
    },
    "options": {
        "draftAndPublish": False,
    },
    "pluginOptions": {},
    "attributes": {
        "place_id": {
            "type": "string",
            "required": True,
        },
        "review_id": {
            "type": "string",
            "required": True,
            "unique": True,
        },
        "author_name": {
            "type": "string",
        },
        "rating": {
            "type": "integer",
        },
        "text": {
            "type": "text",
        },
        "review_url": {
            "type": "string",
        },
        "review_date": {
            "type": "datetime",
        },
        "raw": {
            "type": "json",
        },
    },
}

OPENINGHOURS_SCHEMA = {
    "kind": "collectionType",
    "collectionName": "openinghours",
    "info": {
        "singularName": "openinghour",
        "pluralName": "openinghours",
        "displayName": "Google Business Opening Hours",
        "description": "Opening hours from Google Business Profile",
    },
    "options": {
        "draftAndPublish": False,
    },
    "pluginOptions": {},
    "attributes": {
        "place_id": {
            "type": "string",
            "required": True,
            "unique": True,
        },
        "opening_hours": {
            "type": "json",
        },
        "raw": {
            "type": "json",
        },
    },
}


# TypeScript file templates
CONTROLLER_TEMPLATE = """/**
 * {singular} controller
 */

import {{ factories }} from '@strapi/strapi';

export default factories.createCoreController('api::{singular}.{singular}');
"""

ROUTE_TEMPLATE = """/**
 * {singular} router
 */

import {{ factories }} from '@strapi/strapi';

export default factories.createCoreRouter('api::{singular}.{singular}');
"""

SERVICE_TEMPLATE = """/**
 * {singular} service
 */

import {{ factories }} from '@strapi/strapi';

export default factories.createCoreService('api::{singular}.{singular}');
"""


def create_api_structure(base_path: Path, name: str, schema: dict) -> None:
    """Create complete Strapi API structure for a content type."""
    singular = schema["info"]["singularName"]
    
    # Create directory structure
    api_path = base_path / name
    controllers_path = api_path / "controllers"
    routes_path = api_path / "routes"
    services_path = api_path / "services"
    content_types_path = api_path / "content-types" / singular
    
    # Create directories
    controllers_path.mkdir(parents=True, exist_ok=True)
    routes_path.mkdir(parents=True, exist_ok=True)
    services_path.mkdir(parents=True, exist_ok=True)
    content_types_path.mkdir(parents=True, exist_ok=True)
    
    # Create controller file
    controller_file = controllers_path / f"{singular}.ts"
    with open(controller_file, "w", encoding="utf-8") as f:
        f.write(CONTROLLER_TEMPLATE.format(singular=singular))
    
    # Create route file
    route_file = routes_path / f"{singular}.ts"
    with open(route_file, "w", encoding="utf-8") as f:
        f.write(ROUTE_TEMPLATE.format(singular=singular))
    
    # Create service file
    service_file = services_path / f"{singular}.ts"
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(SERVICE_TEMPLATE.format(singular=singular))
    
    # Create schema file (without outer wrapper)
    schema_file = content_types_path / "schema.json"
    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    
    print(f"✓ Generated {name}:")
    print(f"  - {singular}/controllers/{singular}.ts")
    print(f"  - {singular}/routes/{singular}.ts")
    print(f"  - {singular}/services/{singular}.ts")
    print(f"  - {singular}/content-types/{singular}/schema.json")


def main() -> None:
    """Generate Strapi API structure for reviews and opening hours collections."""
    schemas = {
        "review": REVIEW_SCHEMA,
        "openinghour": OPENINGHOURS_SCHEMA,
    }
    
    # Determine base path (create in generated_strapi_types)
    script_dir = Path(__file__).parent.parent.parent
    base_path = script_dir / "generated_strapi_types"
    base_path.mkdir(exist_ok=True)
    
    print("Generating Strapi API structures...\n")
    
    for name, schema in schemas.items():
        create_api_structure(base_path, name, schema)
        print()
    
    print("Generated files in: generated_strapi_types/")
    print("\nTo use these in Strapi:")
    print("1. Copy the folders to your Strapi project:")
    print("   cp -r generated_strapi_types/review/* <strapi-project>/src/api/review/")
    print("   cp -r generated_strapi_types/openinghour/* <strapi-project>/src/api/openinghour/")
    print("2. Restart Strapi")
    print("3. The collections will be auto-created based on these schemas")


if __name__ == "__main__":
    main()
