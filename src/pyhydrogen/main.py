"""pyHydrogen application entry point.

Usage
-----
From the repository root::

    cd src
    python -m pyhydrogen.main

Or, with PYTHONPATH set::

    PYTHONPATH=src python -m pyhydrogen.main
"""

import os
import webview

from pyhydrogen.api.bridge import HydrogenAPI


def main() -> None:
    """Create the pywebview window and start the GUI event loop."""
    api = HydrogenAPI()

    # Resolve the path to the frontend assets directory so that
    # pywebview's built-in HTTP server can serve CSS / JS correctly.
    gui_assets = os.path.join(os.path.dirname(__file__), "gui", "assets")
    html_path = os.path.join(gui_assets, "index.html")

    webview.create_window(
        title="pyHydrogen — Hydrogen Atom Wavefunctions",
        url=html_path,
        js_api=api,
        width=1280,
        height=800,
        min_size=(960, 640),
        background_color="#1a1a2e",
    )

    # debug=True opens the browser dev-tools (useful during development).
    webview.start(debug=False)


if __name__ == "__main__":
    main()
