# For Python projects
- follow best practices for maintainable and scalable code
- prefer using uvicorn instead of pip for installing dependencies and running the project
- Keep track of the "launch.json" and "task.json" configurations, so the project can be run with the VsCode Debugger 
- The "launch.json" should be configured in the root of the project, so it can be used by all the projects in the workspace.
- The "launch.json" configuration should be on "workspace" scope of VsCode, so it can be used by all the projects in the workspace

## Architecture
- Always use the "pyproject.toml" file
- make sure all secrets are stored in environment variables and not hardcoded in the codebase
- use .env files for local development and ensure they are included in .gitignore
- make sure to keep an .env.example file with all the required environment variables for the project 

## Code Quality
- make sure to use a consistent code style and follow PEP 8 guidelines
- Prefer small pure functions
- Avoid premature optimization


# Virtualisation

## Dockerfiles
- Use multi-stage builds to keep the final image size small
- Use official base images when possible
- Avoid installing unnecessary packages in the Docker image
- Use .dockerignore to exclude files and directories that are not needed in the Docker image
- Make sure to create a non-root user in the Dockerfile and run the application as that user for better security
- Use environment variables for configuration in the Dockerfile and avoid hardcoding values