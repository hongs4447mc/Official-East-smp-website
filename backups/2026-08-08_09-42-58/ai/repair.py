from pathlib import Path
import json

# ==========================================
# EAST SMP AI REPAIR PLANNER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMPACT_FILE = PROJECT_ROOT / "reports" / "impact.json"
REPAIR_FILE = PROJECT_ROOT / "reports" / "repair-plan.json"


def load_impact():

    if not IMPACT_FILE.exists():
        print("[ERROR] impact.json was not found.")
        print(f"Expected: {IMPACT_FILE}")
        return None

    try:

        with IMPACT_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:

        print("[ERROR] impact.json contains invalid JSON.")
        print(error)

        return None

    except OSError as error:

        print("[ERROR] Could not read impact.json.")
        print(error)

        return None


def determine_priority(issue):

    name = issue.get("name", "Unknown issue")

    if name == "Console Error Detector":
        return "HIGH"

    if name == "Load Speed Rating":
        return "LOW"

    return "MEDIUM"


def create_repair(issue):

    name = issue.get("name", "Unknown issue")
    details = issue.get("details", "")

    priority = determine_priority(issue)

    # ------------------------------------------
    # Console error
    # ------------------------------------------

    if name == "Console Error Detector":

        return {
            "issue": name,
            "priority": priority,
            "status": "INVESTIGATION_REQUIRED",

            "problem": details,

            "proposed_action": [
                "Identify the exact URL returning 404.",
                "Check the corresponding Astro route.",
                "Check navigation links pointing to that route.",
                "Check layout components for incorrect paths.",
                "Check whether the development server is serving the route.",
                "Re-run the scanner after investigation."
            ],

            "automatic_modification": False,

            "safety_reason":
                "The exact source of the 404 must be identified before modifying routing or navigation."
        }

    # ------------------------------------------
    # Speed
    # ------------------------------------------

    if name == "Load Speed Rating":

        return {
            "issue": name,
            "priority": priority,
            "status": "INVESTIGATION_REQUIRED",

            "problem": details,

            "proposed_action": [
                "Verify the speed-test logic.",
                "Confirm that the reported response time is valid.",
                "Check whether the pass/fail threshold is working correctly.",
                "Do not modify website assets yet.",
                "Re-run the scanner after correcting the test logic."
            ],

            "automatic_modification": False,

            "safety_reason":
                "The reported result is 3ms - Excellent, so changing website files could be unnecessary."
        }

    # ------------------------------------------
    # Unknown issue
    # ------------------------------------------

    return {
        "issue": name,
        "priority": priority,
        "status": "INVESTIGATION_REQUIRED",

        "problem": details,

        "proposed_action": [
            "Investigate the issue.",
            "Identify affected files.",
            "Analyze dependencies.",
            "Do not modify files automatically."
        ],

        "automatic_modification": False,

        "safety_reason":
            "The scanner does not yet have enough information to safely modify the project."
    }


def main():

    impact = load_impact()

    if impact is None:
        return

    issues = impact.get("issues", [])

    repair_plan = []

    print()
    print("==========================================")
    print(" EAST SMP AI REPAIR PLANNER")
    print("==========================================")
    print()

    print(f"Problems detected: {len(issues)}")
    print()

    for issue in issues:

        repair = create_repair(issue)

        repair_plan.append(repair)

        print(f"[ISSUE] {repair['issue']}")
        print(f"[PRIORITY] {repair['priority']}")
        print(f"[STATUS] {repair['status']}")
        print()

        print("[PROPOSED ACTION]")

        for action in repair["proposed_action"]:
            print(f"- {action}")

        print()

        print("[SAFETY]")
        print(repair["safety_reason"])

        print()
        print("------------------------------------------")
        print()

    REPAIR_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with REPAIR_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "repair_count": len(repair_plan),
                "automatic_modification_allowed": False,
                "repairs": repair_plan
            },
            file,
            indent=2
        )

    print(f"Repair plan saved: {REPAIR_FILE}")


if __name__ == "__main__":
    main()
