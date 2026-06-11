from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.evals.cloud_extraction_normalizer import normalize_cloud_extractions


if __name__ == "__main__":
    import json

    print(json.dumps(normalize_cloud_extractions(), indent=2))
