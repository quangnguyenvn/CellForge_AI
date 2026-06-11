from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.evals.reporting import update_baseline


if __name__ == "__main__":
    path = update_baseline()
    print(f"Updated evaluation baseline: {path}")
