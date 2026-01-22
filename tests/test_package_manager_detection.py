"""Tests for package manager detection functionality."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from react_router_routes.generate import detect_package_manager


def test_detect_package_manager_bun_lockfile(tmp_path: Path) -> None:
    """Test detection when bun.lockb exists and bun is available."""
    # Create bun lockfile
    (tmp_path / "bun.lockb").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = detect_package_manager(tmp_path)

        # Should detect bun based on lockfile
        assert result == "bun"
        mock_run.assert_called_with(
            ["bun", "--version"], capture_output=True, check=True
        )


def test_detect_package_manager_pnpm_lockfile(tmp_path: Path) -> None:
    """Test detection when pnpm-lock.yaml exists and pnpm is available."""
    # Create pnpm lockfile
    (tmp_path / "pnpm-lock.yaml").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = detect_package_manager(tmp_path)

        # Should detect pnpm based on lockfile
        assert result == "pnpm"
        mock_run.assert_called_with(
            ["pnpm", "--version"], capture_output=True, check=True
        )


def test_detect_package_manager_npm_lockfile(tmp_path: Path) -> None:
    """Test detection when package-lock.json exists and npm is available."""
    # Create npm lockfile
    (tmp_path / "package-lock.json").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = detect_package_manager(tmp_path)

        # Should detect npm based on lockfile
        assert result == "npm"
        mock_run.assert_called_with(
            ["npm", "--version"], capture_output=True, check=True
        )


def test_detect_package_manager_multiple_lockfiles(tmp_path: Path) -> None:
    """Test priority order when multiple lockfiles exist."""
    # Create multiple lockfiles
    (tmp_path / "bun.lockb").touch()
    (tmp_path / "pnpm-lock.yaml").touch()
    (tmp_path / "package-lock.json").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = detect_package_manager(tmp_path)

        # Should prioritize bun first
        assert result == "bun"
        mock_run.assert_called_with(
            ["bun", "--version"], capture_output=True, check=True
        )


def test_detect_package_manager_lockfile_but_not_available(tmp_path: Path) -> None:
    """Test fallback when lockfile exists but package manager is not available."""
    # Create bun lockfile but bun is not available
    (tmp_path / "bun.lockb").touch()
    (tmp_path / "pnpm-lock.yaml").touch()

    def mock_run_side_effect(args, **kwargs):
        if args[0] == "bun":
            raise FileNotFoundError("bun not found")
        elif args[0] == "pnpm":
            # pnpm is available
            return subprocess.CompletedProcess(args, 0)
        else:
            raise FileNotFoundError()

    with patch("subprocess.run", side_effect=mock_run_side_effect):
        result = detect_package_manager(tmp_path)

        # Should fall back to pnpm since bun is not available
        assert result == "pnpm"


def test_detect_package_manager_no_lockfiles(tmp_path: Path) -> None:
    """Test detection when no lockfiles exist - should check availability in order."""

    def mock_run_side_effect(args, **kwargs):
        if args[0] == "bun":
            raise FileNotFoundError("bun not found")
        elif args[0] == "pnpm":
            # pnpm is available
            return subprocess.CompletedProcess(args, 0)
        elif args[0] == "npm":
            return subprocess.CompletedProcess(args, 0)
        else:
            raise FileNotFoundError()

    with patch("subprocess.run", side_effect=mock_run_side_effect):
        result = detect_package_manager(tmp_path)

        # Should detect pnpm as first available in priority order
        assert result == "pnpm"


def test_detect_package_manager_fallback_to_npm(tmp_path: Path) -> None:
    """Test ultimate fallback to npm when nothing else is available."""

    def mock_run_side_effect(args, **kwargs):
        if args[0] in ["bun", "pnpm"]:
            raise FileNotFoundError(f"{args[0]} not found")
        else:
            # npm (or anything else) returns successfully
            return subprocess.CompletedProcess(args, 0)

    with patch("subprocess.run", side_effect=mock_run_side_effect):
        result = detect_package_manager(tmp_path)

        # Should fallback to npm
        assert result == "npm"


def test_detect_package_manager_nothing_available(tmp_path: Path) -> None:
    """Test behavior when no package managers are available."""

    with patch("subprocess.run", side_effect=FileNotFoundError("not found")):
        result = detect_package_manager(tmp_path)

        # Should still return npm as the ultimate fallback
        assert result == "npm"
