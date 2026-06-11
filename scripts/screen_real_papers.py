from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
local_deps = ROOT / ".python-deps"
if local_deps.exists():
    sys.path.insert(0, str(local_deps))

from services.evals.paper_screening import main


if __name__ == "__main__":
    main()
