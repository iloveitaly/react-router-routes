"""Package entrypoint for the react-router-routes CLI.

Running the installed script (configured via [project.scripts]) will
invoke Typer's CLI defined in `generate.py`.
"""

import logging
import os

from .generate import app

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
)

logger = logging.getLogger(__name__)


def main() -> None:  # console_scripts entry point
    """Dispatch to the Typer application.

    Example:
        react-router-routes generate-route-types ./js-app ./routes_typing.py
    """
    app()


__all__ = ["main", "app"]
