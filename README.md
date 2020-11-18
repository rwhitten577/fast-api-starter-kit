## Cookiecutter FastAPI Starter Kit
#### An opinionated starter kit for quickly building FastAPI services with PostgreSQL, SQLAlchemy, Alembic.

### Features
* FastAPI for service creation
* Uvicorn ASGI server for local development, Mangum for deploying to AWS Lambda
* SQLAlchemy & Alembic for ORM/database migrations
* Default database is PostgreSQL but easily configurable to use MySQL, etc. 
* Uses AWS Cognito for Auth - decodes JWT tokens from Cognito. Easily configured to decode tokens generated elsewhere. 

### Installation
1. Install [poetry](https://python-poetry.org/), used for managing dependencies and virtual environments.
1. Install cookiecutter on your machine:
    ```
    $ pip install cookiecutter
    ```
1. Run cookiecutter to clone the project to your current director: 
    ```
    $ cookiecutter https://github.com/rwhitten577/fast-api-starter-kit.git
    ```
1. Follow prompts to name your project. `git_repo_name` should be what your future repo will be (using dashes), 
and project_name will be used to name your Python package (using underscores).
    ```
    git_repo_name [example-repo-name-using-dashes]: your-repo-name-here
    project_name [example_project_name_using_underscores]: your_project_name
    ```

1. CD to your new project and install dependencies with `poetry install`. 

1. Run tests with `pytest`.
