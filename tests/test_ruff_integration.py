from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from react_router_routes.generate import generate_route_types, lint_generated_file


def test_ruff_integration_when_available(tmp_path: Path) -> None:
    """Test that ruff is called when available."""
    json_path = Path(__file__).parent / "react-router.json"
    output = tmp_path / "routes_typing.py"

    # Generate with ruff integration
    generate_route_types(
        output_file=output,
        directory=None,
        json_file=json_path,
    )

    content = output.read_text()

    # Verify basic content is still there
    assert '"/home"' in content
    assert "def react_router_path" in content

    # If ruff is available, check that TypedDict and NotRequired are not imported
    # (they should be removed by ruff since they're unused in test data)
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
        # ruff is available, so imports should be cleaned
        assert "TypedDict" not in content or "NotRequired" not in content
    except (subprocess.CalledProcessError, FileNotFoundError):
        # ruff not available, test still passes
        pass


def test_ruff_integration_when_not_available(tmp_path: Path) -> None:
    """Test that generation works gracefully when ruff is not available."""
    json_path = Path(__file__).parent / "react-router.json"
    output = tmp_path / "routes_typing.py"

    # Mock subprocess to simulate ruff not being available
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        generate_route_types(
            output_file=output,
            directory=None,
            json_file=json_path,
        )

    content = output.read_text()

    # Verify generation still works
    assert '"/home"' in content
    assert "def react_router_path" in content
    assert output.exists()


def test_lint_generated_file_direct(tmp_path: Path) -> None:
    """Test the lint_generated_file function directly."""
    test_file = tmp_path / "test.py"

    # Create a file with formatting issues
    test_file.write_text("import os,sys\n\ndef test():pass\n")

    # Call lint function
    lint_generated_file(test_file)

    content = test_file.read_text()

    # Check if file still exists and has content
    assert test_file.exists()
    assert "def test" in content

    try:
        # If ruff is available, check that formatting improved
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
        # Should have proper formatting and removed unused imports
        assert "def test():" in content
        assert "os,sys" not in content  # Should be removed or reformatted
    except (subprocess.CalledProcessError, FileNotFoundError):
        # ruff not available, test still passes
        pass


def test_lint_generated_file_with_ruff_failure(tmp_path: Path) -> None:
    """Test that lint function handles ruff failures gracefully."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    # Mock ruff to fail
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ruff")):
        lint_generated_file(test_file)

    # File should still exist and be unchanged
    assert test_file.exists()
    assert "def test(): pass" in test_file.read_text()
