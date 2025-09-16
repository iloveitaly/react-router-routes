"""Test react-router-routes."""

import react_router_routes


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(react_router_routes.__name__, str)