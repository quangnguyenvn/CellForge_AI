from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.evals.local_eval import print_report, run_auditor_eval


if __name__ == "__main__":
    print_report(run_auditor_eval())
