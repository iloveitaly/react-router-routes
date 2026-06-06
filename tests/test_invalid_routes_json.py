from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from react_router_routes.generate import generate_route_types


def test_generate_route_types_surfaces_invalid_json_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "pnpm-lock.yaml").touch()

    output_file = tmp_path / "output.py"

    with patch("react_router_routes.generate.subprocess.run") as mock_run:

        def mock_run_side_effect(args, **kwargs):
            if args == ["pnpm", "--version"]:
                return subprocess.CompletedProcess(args, 0, stdout="7.0.0")

            if args == ["pnpm", "react-router", "routes", "--json"]:
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout='CLI info\n[{"id": "root", "path": "", "file": "root.tsx"}]',
                )

            raise FileNotFoundError(f"unexpected command: {args}")

        mock_run.side_effect = mock_run_side_effect

        with pytest.raises(typer.Exit):
            generate_route_types(
                output_file=output_file,
                directory=project_dir,
                json_file=None,
            )

    captured = capsys.readouterr()
    assert "Error parsing JSON from `pnpm react-router routes --json`" in captured.err
    assert "line 1, column 1" in captured.err
    assert (
        "Run this manually in your app directory to inspect the raw output:"
        in captured.err
    )
    assert f"cd {project_dir}" in captured.err
    assert "pnpm react-router routes --json" in captured.err
