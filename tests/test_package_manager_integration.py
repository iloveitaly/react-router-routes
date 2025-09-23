"""Integration tests for package manager detection in CLI."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from react_router_routes.generate import generate_route_types


def test_generate_route_types_detects_package_manager(tmp_path: Path) -> None:
    """Test that generate_route_types properly detects and uses package manager."""
    # Create a directory with a pnpm lockfile
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "pnpm-lock.yaml").touch()
    
    output_file = tmp_path / "output.py"
    
    # Mock the subprocess.run calls
    with patch("react_router_routes.generate.subprocess.run") as mock_run:
        def mock_run_side_effect(args, **kwargs):
            if args == ["pnpm", "--version"]:
                return subprocess.CompletedProcess(args, 0, stdout="7.0.0")
            elif args == ["pnpm", "react-router", "routes", "--json"]:
                return subprocess.CompletedProcess(
                    args, 0, 
                    stdout='[{"id": "root", "path": "", "file": "root.tsx", "children": [{"id": "routes/test", "path": "/test", "file": "routes/test.tsx"}]}]'
                )
            elif args == ["ruff", "--version"]:
                # ruff version check for linting
                raise FileNotFoundError("ruff not available")
            else:
                # Handle any other ruff calls
                raise FileNotFoundError(f"Command not found: {args}")
        
        mock_run.side_effect = mock_run_side_effect
        
        # Call the function
        generate_route_types(
            output_file=output_file,
            directory=project_dir,
            json_file=None,
        )
        
        # Verify pnpm was detected and used
        mock_run.assert_any_call(["pnpm", "--version"], capture_output=True, check=True)
        mock_run.assert_any_call(
            ["pnpm", "react-router", "routes", "--json"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        
        # Verify output file was created with proper content
        assert output_file.exists()
        content = output_file.read_text()
        assert '"/test"' in content


def test_generate_route_types_falls_back_to_npm(tmp_path: Path) -> None:
    """Test that generate_route_types falls back to npm when preferred manager is not available."""
    # Create a directory with a bun lockfile, but bun is not available
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "bun.lockb").touch()
    
    output_file = tmp_path / "output.py"
    
    # Mock the subprocess.run calls
    with patch("react_router_routes.generate.subprocess.run") as mock_run:
        def mock_run_side_effect(args, **kwargs):
            if args == ["bun", "--version"]:
                raise FileNotFoundError("bun not found")
            elif args == ["pnpm", "--version"]:
                raise FileNotFoundError("pnpm not found")
            elif args == ["npm", "--version"]:
                return subprocess.CompletedProcess(args, 0, stdout="8.0.0")
            elif args == ["npm", "react-router", "routes", "--json"]:
                return subprocess.CompletedProcess(
                    args, 0, 
                    stdout='[{"id": "root", "path": "", "file": "root.tsx", "children": [{"id": "routes/fallback", "path": "/fallback", "file": "routes/fallback.tsx"}]}]'
                )
            elif args == ["ruff", "--version"]:
                # ruff version check for linting
                raise FileNotFoundError("ruff not available")
            else:
                raise FileNotFoundError(f"Unexpected command: {args}")
        
        mock_run.side_effect = mock_run_side_effect
        
        # Call the function
        generate_route_types(
            output_file=output_file,
            directory=project_dir,
            json_file=None,
        )
        
        # Verify npm was used as fallback
        mock_run.assert_any_call(["npm", "--version"], capture_output=True, check=True)
        mock_run.assert_any_call(
            ["npm", "react-router", "routes", "--json"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        
        # Verify output file was created
        assert output_file.exists()
        content = output_file.read_text()
        assert '"/fallback"' in content


def test_generate_route_types_handles_command_failure(tmp_path: Path) -> None:
    """Test that generate_route_types properly handles command failures."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "package-lock.json").touch()
    
    output_file = tmp_path / "output.py"
    
    with patch("react_router_routes.generate.subprocess.run") as mock_run:
        def mock_run_side_effect(args, **kwargs):
            if args == ["npm", "--version"]:
                return subprocess.CompletedProcess(args, 0, stdout="8.0.0")
            elif args == ["npm", "react-router", "routes", "--json"]:
                return subprocess.CompletedProcess(
                    args, 1, stderr="react-router not found"
                )
            else:
                raise FileNotFoundError(f"Command not found: {args}")
        
        mock_run.side_effect = mock_run_side_effect
        
        # Call should raise typer.Exit due to command failure
        with pytest.raises(typer.Exit):
            generate_route_types(
                output_file=output_file,
                directory=project_dir,
                json_file=None,
            )