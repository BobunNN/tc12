Repo init commands



# docs/

This folder is for documentation related to extending and maintaining the FastAPI template.

## Init commands
>>>>>>> dev
>>>>>>> main

````[bash]
git init
uv init --python "python>=[version]"
uv add fastapi --extra standard 

````
=======
>>>>>>> main
````

## Extending the Template

- Add new routers in `src/app/` as needed.
- Use environment variables for configuration (see `.env.example`).
- Add dependencies to `pyproject.toml`.
- For database or authentication, create new modules and keep the core template minimal.

## Documentation Tools

- Consider using Sphinx or MkDocs for auto-generating documentation from your code and docstrings.

## Testing

- Place your tests in the `tests/` folder.
- Use `pytest` for running tests.

## Linting & Formatting

- Pre-commit hooks are configured in `.pre-commit-config.yaml`.
- Run `pre-commit install` after cloning to enable hooks.
