"""Legacy entrypoint.

Web UI is now deprecated from core package scope and moved to `examples/webapp/app.py`.
"""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    msg = (
        "Legacy app.py is deprecated.\n"
        "Use the CLI: `lunardem generate ...`\n"
        "Or run the demo web app at examples/webapp/app.py.\n"
    )
    print(msg)
    demo_path = Path("examples/webapp/app.py")
    if demo_path.exists():
        print(f"Demo app available at: {demo_path}")


if __name__ == "__main__":
    main()
