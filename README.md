react-router-routes
====================

Generate strongly-typed Python helpers (TypedDict param objects + overloads) from a React Router v6+ route tree. This is useful when a Python backend, worker, or test suite needs to construct URLs that stay in sync with a JavaScript/TypeScript frontend using React Router.

What you get
------------
Given a React Router project, the CLI runs `pnpm react-router routes --json`, walks the returned route objects, and produces a Python module containing:

* `RoutePaths` Literal of every concrete route pattern (e.g. `/users/:userId?`, `/files/*`).
* Per-route `TypedDict` classes containing snake_case parameter keys.
* Overloaded `react_router_path()` to build a relative path with validation + percent-encoding.
* Overloaded `react_router_url()` to prepend a base URL (explicit argument or `BASE_URL` env var).

Installation
------------
Using uv (recommended):

```bash
uv add react-router-routes
```

Or with pip:

```bash
pip install react-router-routes
```

Prerequisites
-------------
Your JS project must have `react-router` and the `pnpm react-router routes --json` command available (React Router v6+ data APIs). The Python process must run inside (or have access to) that project directory so the CLI can execute the command.

CLI Usage
---------
The script entry point is named `react-router-routes` (see `pyproject.toml`). Run:

```bash
react-router-routes generate-route-types /path/to/js/app /path/to/output/routes_typing.py
```

Example:

```bash
react-router-routes generate-route-types ./frontend ./routes_typing.py
```

Then import the generated module in Python code:

```python
from routes_typing import react_router_path, react_router_url, RoutePaths

react_router_path('/users/:userId', {'user_id': 123})  # -> '/users/123'
react_router_url('/files/*', {'splat': 'docs/readme.md'}, base_url='https://example.com')
```

Environment Variables
---------------------
* `BASE_URL` (optional) – If set and you omit `base_url` when calling `react_router_url`, this value is prepended. If missing the function returns the path and logs a warning.
* `LOG_LEVEL` (optional) – Standard Python logging level (INFO, DEBUG, etc.).

Development
-----------
Clone and install dev deps:

```bash
uv sync --all-extras --group dev
```

Run tests:

```bash
pytest -q
```

Release process
---------------
This project uses `uv` for building and publishing. Adjust version in `pyproject.toml`, then build and publish as desired.

License
-------
MIT (see repository).
