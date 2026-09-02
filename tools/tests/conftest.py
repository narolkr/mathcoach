import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
ROOT = TOOLS.parent

# Make `mathcoach` importable, and the chapter packages under content/.
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "content" / "chapters" / "09-chain-rule"))
