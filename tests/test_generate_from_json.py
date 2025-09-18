from __future__ import annotations

from pathlib import Path

from react_router_routes.generate import generate_route_types  # type: ignore


def test_generate_from_json(tmp_path: Path) -> None:
    json_path = Path(__file__).parent / "react-router.json"
    output = tmp_path / "routes_typing.py"

    # Invoke the installed console script via python -m to ensure we use local package.
    # Equivalent to: react-router-routes generate-route-types ...
    # Call the command function directly (Typer would do this when invoked via CLI)
    generate_route_types(
        output_file=output,
        directory=None,
        json_file=json_path,
    )

    content = output.read_text()
    # Basic assertions about generated content
    assert '"/home"' in content
    assert '"/form"' in content
    # Root slash pattern should appear
    assert '"/"' in content

    # ensure path helper exists
    assert "def react_router_path" in content
    assert "def react_router_url" in content
