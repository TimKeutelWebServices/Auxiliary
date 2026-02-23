#!/usr/bin/env python
"""Generate Strapi schema for the opening hours collection."""

import json
from pathlib import Path


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

    api_path = base_path / name
    controllers_path = api_path / "controllers"
    routes_path = api_path / "routes"
    services_path = api_path / "services"
    content_types_path = api_path / "content-types" / singular

    controllers_path.mkdir(parents=True, exist_ok=True)
    routes_path.mkdir(parents=True, exist_ok=True)
    services_path.mkdir(parents=True, exist_ok=True)
    content_types_path.mkdir(parents=True, exist_ok=True)

    (controllers_path / f"{singular}.ts").write_text(
        CONTROLLER_TEMPLATE.format(singular=singular), encoding="utf-8"
    )
    (routes_path / f"{singular}.ts").write_text(
        ROUTE_TEMPLATE.format(singular=singular), encoding="utf-8"
    )
    (services_path / f"{singular}.ts").write_text(
        SERVICE_TEMPLATE.format(singular=singular), encoding="utf-8"
    )
    (content_types_path / "schema.json").write_text(
        json.dumps(schema, indent=2), encoding="utf-8"
    )

    print(f"✓ Generated {name}/")


def main() -> None:
    """Generate Strapi API structure for opening hours collection."""
    script_dir = Path(__file__).parent.parent.parent
    base_path = script_dir / "generated_strapi_types"
    base_path.mkdir(exist_ok=True)

    print("Generating Strapi API structure …\n")
    create_api_structure(base_path, "openinghour", OPENINGHOURS_SCHEMA)

    print("\nTo use in Strapi:")
    print("  cp -r generated_strapi_types/openinghour/* <strapi>/src/api/openinghour/")
    print("  Restart Strapi.")


if __name__ == "__main__":
    main()
