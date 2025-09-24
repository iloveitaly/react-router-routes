from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from react_router_routes.generate import generate_route_types


def test_url_params_functionality(tmp_path: Path) -> None:
    """Test the url_params functionality in generated code."""
    json_path = Path(__file__).parent / "react-router.json"
    output = tmp_path / "routes_typing.py"

    # Generate the module
    generate_route_types(
        output_file=output,
        directory=None,
        json_file=json_path,
    )

    # Import the generated module dynamically
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("routes_typing", output)
    assert spec is not None
    assert spec.loader is not None
    routes_typing = importlib.util.module_from_spec(spec)
    sys.modules["routes_typing"] = routes_typing
    spec.loader.exec_module(routes_typing)

    # Test basic url_params functionality
    result = routes_typing.react_router_path("/home", url_params={"page": "1", "sort": "name"})
    assert result == "/home?page=1&sort=name"

    # Test url_params with react_router_url
    result = routes_typing.react_router_url("/home", base_url="https://example.com", url_params={"foo": "bar"})
    assert result == "https://example.com/home?foo=bar"

    # Test that None url_params works like before
    result = routes_typing.react_router_path("/home", url_params=None)
    assert result == "/home"

    # Test that empty dict url_params works like before  
    result = routes_typing.react_router_path("/home", url_params={})
    assert result == "/home"

    # Test special characters are encoded properly
    result = routes_typing.react_router_path("/home", url_params={"query": "hello world", "special": "a&b"})
    assert result == "/home?query=hello+world&special=a%26b"

    # Test backward compatibility - can call without url_params
    result = routes_typing.react_router_path("/home")
    assert result == "/home"

    result = routes_typing.react_router_url("/home", base_url="https://example.com")
    assert result == "https://example.com/home"


def test_url_params_with_path_parameters(tmp_path: Path) -> None:
    """Test url_params with routes that have path parameters."""
    # Create a test JSON file with parameterized routes
    test_json = tmp_path / "test_routes.json"
    test_json.write_text("""[
      {
        "id": "root",
        "path": "",
        "file": "root.tsx",
        "children": [
          {
            "id": "routes/user",
            "path": "/user/:userId",
            "file": "routes/user.tsx"
          },
          {
            "id": "routes/files",
            "path": "/files/*",
            "file": "routes/files.tsx"
          },
          {
            "id": "routes/optional",
            "path": "/optional/:id?",
            "file": "routes/optional.tsx"
          }
        ]
      }
    ]""")

    output = tmp_path / "routes_typing.py"

    # Generate the module
    generate_route_types(
        output_file=output,
        directory=None,
        json_file=test_json,
    )

    # Import the generated module dynamically
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("routes_typing_params", output)
    assert spec is not None
    assert spec.loader is not None
    routes_typing = importlib.util.module_from_spec(spec)
    sys.modules["routes_typing_params"] = routes_typing
    spec.loader.exec_module(routes_typing)

    # Test url_params with path parameters
    result = routes_typing.react_router_path("/user/:userId", {"user_id": "123"}, url_params={"tab": "profile"})
    assert result == "/user/123?tab=profile"

    # Test url_params with splat routes
    result = routes_typing.react_router_path("/files/*", {"splat": "docs/readme.md"}, url_params={"download": "true"})
    assert result == "/files/docs/readme.md?download=true"

    # Test url_params with optional parameters
    result = routes_typing.react_router_path("/optional/:id?", {"id": "456"}, url_params={"edit": "true"})
    assert result == "/optional/456?edit=true"

    # Test url_params with optional parameters not provided
    result = routes_typing.react_router_path("/optional/:id?", {}, url_params={"create": "true"})
    assert result == "/optional?create=true"