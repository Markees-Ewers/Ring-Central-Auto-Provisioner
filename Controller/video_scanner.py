"""Compatibility module for the application controller.

Author: Markees Ewers
Responsibility: Preserve the legacy launcher path while delegating startup to
the application controller.
"""

from Controller.application_controller import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
