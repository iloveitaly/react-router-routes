"""Package entrypoint for the react-router-routes CLI.

Running the installed script (configured via [project.scripts]) will
invoke Typer's CLI defined in `generate.py`.
"""

from structlog_config import configure_logger

from .generate import main as _main

logger = configure_logger()


def main() -> None:  # console_scripts entry point
    """Dispatch to the Typer application.

    Example:
        react-router-routes ./routes_typing.py --directory ./js-app
    """
    _main()


__all__ = ["main"]