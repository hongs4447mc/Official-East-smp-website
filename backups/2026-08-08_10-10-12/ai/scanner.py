from pathlib import Path
import json


# ==========================================
# EAST SMP AI SCANNER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "scanner.json"


def load_report():
    """Load the JavaScript scanner report."""

    if not REPORT_FILE.exists():
        print("[ERROR] scanner.json was not found.")
        print(f"Expected: {REPORT_FILE}")
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


def analyze_report(report):
    """Analyze the existing scanner results."""

    passed = 0
    failed = 0

    print()
    print("==========================================")
    print(" EAST SMP AI SCANNER")
    print("==========================================")
    print()

    for result in report:

        name = result.get("name", "Unknown")
        status = result.get("passed", False)
        details = result.get("details", "")

        if status:
            passed += 1
            print(f"[PASS] {name}")

        else:
            failed += 1
            print(f"[FAIL] {name}")
            print(f"       {details}")

    total = passed + failed

    if total > 0:
        score = round((passed / total) * 100)
    else:
        score = 0

    print()
    print("==========================================")
    print(" AI ANALYSIS")
    print("==========================================")
    print()

    print(f"Tests passed : {passed}")
    print(f"Tests failed : {failed}")
    print(f"Health score : {score}%")

    print()

    if failed == 0:
        print("[AI] Project looks healthy.")

    elif failed == 1:
        print("[AI] 1 issue requires attention.")

    else:
        print(f"[AI] {failed} issues require attention.")

    print()
    print("==========================================")


def main():
    report = load_report()

    if report is None:
        return

    analyze_report(report)


if __name__ == "__main__":
    main()
    