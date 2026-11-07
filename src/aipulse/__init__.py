"""AI Pulse: a stdlib-only toolkit over the daily AI-industry digests.

Modules in this package import each other with flat imports
(`from models import Digest`) so each file can also be run directly as a
script (`python src/aipulse/archive.py`). Importing the package adds this
directory to sys.path once, so the same modules also work as
`import aipulse.archive` from code that puts src/ on its path.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

__version__ = "0.2.0"
