from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.evals.publication_validation import main


if __name__ == "__main__":
    main()
