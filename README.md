# Generate Typed Python URL Helpers from React Router Routes

Generate strongly-typed Python helpers (TypedDict param objects + overloads) from a React Router v6+ route tree. This is useful when a Python backend, worker, or test suite needs to construct URLs that stay in sync with a JavaScript/TypeScript frontend using React Router.

[Take a look at this project for a live usage example.](https://github.com/iloveitaly/python-starter-template/blob/0946513b9430c1cd4eb2b115ea596ae2ffc6994a/just/python.just#L61-L62)

## How it works

Given a React Router project, the CLI either:

* Auto-detects your package manager (bun, pnpm, or npm) and runs `<package-manager> react-router routes --json` (if you pass `--directory`), or
* Reads a pre-generated JSON file (if you pass `--json-file`)

It walks the returned route objects and produces a Python module containing:

* `RoutePaths` Literal of every concrete route pattern (e.g. `/users/:userId?`, `/files/*`).
* Per-route `TypedDict` classes containing snake_case parameter keys.
* Overloaded `react_router_path()` to build a relative path with validation + percent-encoding.
* Overloaded `react_router_url()` to prepend a base URL (explicit argument or `BASE_URL` env var).
* Optional `url_params` argument on both functions to append query string parameters.

## Installation

Using uv (recommended):

```bash
uv add react-router-routes
```

## Prerequisites

Your JS project must have `react-router` and a package manager with the `react-router routes --json` command available (React Router v6+ data APIs). The tool automatically detects your package manager (bun, pnpm, or npm) based on lockfiles and availability. The Python process must run inside (or have access to) that project directory so the CLI can execute the command.

## CLI Usage

The script entry point is named `react-router-routes` (see `pyproject.toml`).

Two ways to supply routes:

1. Have the tool invoke `<package-manager> react-router routes --json` by providing a directory (auto-detects bun, pnpm, or npm):

```bash
react-router-routes ./routes_typing.py --directory ./frontend
```

1. Provide an existing JSON file (output of `pnpm react-router routes --json`):

```bash
react-router-routes ./routes_typing.py --json-file tests/react-router.json
```

Then import the generated module in Python code:

```python
from routes_typing import react_router_path, react_router_url, RoutePaths

# Basic path generation
react_router_path('/users/:userId', {'user_id': 123})  # -> '/users/123'

# URL generation with base URL
react_router_url('/files/*', {'splat': 'docs/readme.md'}, base_url='https://example.com')
# -> 'https://example.com/files/docs/readme.md'

# Adding query parameters with url_params
react_router_path('/users/:userId', {'user_id': 123}, url_params={'tab': 'profile', 'edit': 'true'})
# -> '/users/123?tab=profile&edit=true'

react_router_url('/home', base_url='https://example.com', url_params={'page': '1', 'sort': 'name'})
# -> 'https://example.com/home?page=1&sort=name'
```


## Environment Variables

* `BASE_URL` (optional) – If set and you omit `base_url` when calling `react_router_url`, this value is prepended. If missing the function returns the path and logs a warning.
* `LOG_LEVEL` (optional) – Standard Python logging level (INFO, DEBUG, etc.).

## [MIT License](LICENSE)
