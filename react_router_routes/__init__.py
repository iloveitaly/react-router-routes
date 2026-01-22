"""Package entrypoint for the react-router-routes CLI.

Running the installed script (configured via [project.scripts]) will
invoke Typer's CLI defined in `generate.py`.
"""

from structlog_config import configure_logger

from .generate import app

logger = configure_logger()


def main() -> None:  # console_scripts entry point
    """Dispatch to the Typer application.

    Example:
        react-router-routes generate-route-types ./js-app ./routes_typing.py
    """
    app()


__all__ = ["main", "app"]
