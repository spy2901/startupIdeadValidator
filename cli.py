import json
import sys

from app.config import load_config
from app.services.analyst import run_analysis


def main():
    print("=== Product Market Analyzer ===\n")

    if len(sys.argv) == 3:
        idea = sys.argv[1]
        audience = sys.argv[2]
    else:
        idea = input("Startup idea: ").strip()
        audience = input("Target audience or subreddit: ").strip()

    if not idea or not audience:
        print("Error: both idea and audience are required.")
        sys.exit(1)

    print("\nAnalyzing... this may take a few seconds.\n")
    config = load_config()
    result = run_analysis(idea=idea, audience=audience, config=config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
