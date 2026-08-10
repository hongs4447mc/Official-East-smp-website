from pathlib import Path
import json


# ==========================================
# EAST SMP AI ANALYZER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "scanner.json"


def load_report():
    """Load the latest scanner report."""

    if not REPORT_FILE.exists():
        print("[ERROR] scanner.json was not found.")
        return None

    try:
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        print("[ERROR] scanner.json contains invalid JSON.")
        print(error)
        return None

    except OSError as error:
        print("[ERROR] Could not read scanner.json.")
        print(error)
        return None


def analyze_issue(result):
    """Analyze one failed scanner result."""

    name = result.get("name", "Unknown")
    details = result.get("details", "")

    print()
    print("------------------------------------------")
    print(f"ISSUE: {name}")
    print("------------------------------------------")
    print(f"Details: {details}")
    print()

    if name == "Console Error Detector":

        print("[AI ANALYSIS]")
        print("A web resource returned HTTP 404.")

        print()
        print("[POSSIBLE CAUSES]")
        print("1. A page or resource does not exist.")
        print("2. A link points to the wrong location.")
        print("3. The Astro development server is not serving the expected route.")
        print("4. A browser request is being made to an incorrect URL.")

        print()
        print("[RECOMMENDED INVESTIGATION]")
        print("Check the requested URL and the corresponding Astro route.")
        print("Do not modify files automatically yet.")

    elif name == "Load Speed Rating":

        print("[AI ANALYSIS]")
        print("The speed test completed successfully, but the scanner")
        print("marked the test as failed.")

        print()
        print("[POSSIBLE CAUSE]")
        print("The speed-test pass/fail condition may not match the")
        print("reported performance result.")

        print()
        print("[RECOMMENDED INVESTIGATION]")
        print("Review the speed-test logic before changing the website.")

    else:

        print("[AI ANALYSIS]")
        print("This issue does not have a specialized analyzer yet.")

        print()
        print("[RECOMMENDED ACTION]")
        print("Inspect the scanner details and source files manually.")


def analyze_report(report):
    """Analyze all failed scanner results."""

    failures = [
        result
        for result in report
        if not result.get("passed", False)
    ]

    print()
    print("==========================================")
    print(" EAST SMP AI ANALYZER")
    print("==========================================")

    print()
    print(f"Problems detected: {len(failures)}")

    if not failures:
        print()
        print("[AI] No problems require analysis.")
        return

    for result in failures:
        analyze_issue(result)

    print()
    print("==========================================")
    print(" ANALYSIS COMPLETE")
    print("==========================================")


def main():

    report = load_report()

    if report is None:
        return

    analyze_report(report)


if __name__ == "__main__":
    main()