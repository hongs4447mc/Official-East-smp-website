from pathlib import Path
import json

# ==========================================
# EAST SMP AI REPAIR PLANNER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMPACT_FILE = PROJECT_ROOT / "reports" / "impact.json"
REPAIR_FILE = PROJECT_ROOT / "reports" / "repair-plan.json"
SCANNER_FILE = PROJECT_ROOT / "reports" / "scanner.json"


# ==========================================
# LOAD IMPACT REPORT
# ==========================================

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


# ==========================================
# LOAD SCANNER REPORT
# ==========================================

def load_scanner():

    if not SCANNER_FILE.exists():
        return None

    try:

        with SCANNER_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None


# ==========================================
# CHECK PROJECT HEALTH
# ==========================================

def project_is_healthy():

    scanner = load_scanner()

    if scanner is None:
        return False

    if not isinstance(scanner, list):
        return False

    if len(scanner) == 0:
        return False

    failed = [
        result
        for result in scanner
        if not result.get("passed", False)
    ]

    return len(failed) == 0


# ==========================================
# DETERMINE PRIORITY
# ==========================================

def determine_priority(issue):

    name = issue.get(
        "name",
        issue.get("issue", "Unknown issue")
    )

    if name == "Console Error Detector":
        return "HIGH"

    if name == "Load Speed Rating":
        return "LOW"

    return "MEDIUM"


# ==========================================
# CREATE REPAIR
# ==========================================

def create_repair(issue):

    # Impact Analyzer uses "issue".
    # Scanner results may use "name".
    name = issue.get(
        "issue",
        issue.get("name", "Unknown issue")
    )

    details = issue.get(
        "details",
        issue.get("problem", "")
    )

    priority = determine_priority({
        "name": name,
        "issue": name
    })

    affected_areas = issue.get(
        "affected_areas",
        []
    )

    risks = issue.get(
        "risks",
        []
    )

    # --------------------------------------
    # Console error
    # --------------------------------------

    if name == "Console Error Detector":

        return {
            "issue": name,
            "priority": priority,
            "status": "INVESTIGATION_REQUIRED",
            "problem": details,

            "affected_areas": affected_areas,

            "risks": risks,

            "proposed_action": [
                "Identify the exact URL returning the 404 error.",
                "Identify the exact missing resource or route.",
                "Check the corresponding Astro route.",
                "Check navigation links pointing to that route.",
                "Check layout components for incorrect paths.",
                "Check scripts and components that may request the missing resource.",
                "Check whether the development server is serving the expected route.",
                "Analyze dependent files before proposing a modification.",
                "Re-run the scanner after investigation."
            ],

            "automatic_modification": False,

            "safety_reason":
                "The exact source of the 404 error must be identified before modifying routing, navigation, scripts, or assets."
        }

    # --------------------------------------
    # Speed
    # --------------------------------------

    if name == "Load Speed Rating":

        return {
            "issue": name,
            "priority": priority,
            "status": "INVESTIGATION_REQUIRED",
            "problem": details,

            "affected_areas": affected_areas,

            "risks": risks,

            "proposed_action": [
                "Verify the speed-test logic.",
                "Confirm that the reported response time is valid.",
                "Check whether the pass/fail threshold is working correctly.",
                "Determine why the scanner marked the speed test as failed.",
                "Do not modify website assets yet.",
                "Analyze dependent files before proposing a modification.",
                "Re-run the scanner after correcting the test logic."
            ],

            "automatic_modification": False,

            "safety_reason":
                "The speed result and scanner threshold must be verified before changing website assets or performance-related code."
        }

    # --------------------------------------
    # Unknown issue
    # --------------------------------------

    return {
        "issue": name,
        "priority": priority,
        "status": "INVESTIGATION_REQUIRED",
        "problem": details,

        "affected_areas": affected_areas,

        "risks": risks,

        "proposed_action": [
            "Investigate the issue.",
            "Identify affected files.",
            "Analyze dependencies.",
            "Analyze dependent impact.",
            "Do not modify files automatically."
        ],

        "automatic_modification": False,

        "safety_reason":
            "The scanner does not yet have enough information to safely modify the project."
    }


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI REPAIR PLANNER")
    print("==========================================")
    print()

    # --------------------------------------
    # Check current scanner health first
    # --------------------------------------

    if project_is_healthy():

        print("[HEALTH CHECK]")
        print("Scanner reports 0 failed tests.")
        print()
        print("[AI] Project is healthy.")
        print("[AI] No repairs are required.")
        print("[SAFETY] No automatic modifications permitted.")
        print()

        repair_plan = {
            "repair_count": 0,
            "automatic_modification_allowed": False,
            "project_status": "HEALTHY",
            "repairs": []
        }

        REPAIR_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with REPAIR_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                repair_plan,
                file,
                indent=2
            )

        print(f"Repair plan saved: {REPAIR_FILE}")

        return

    # --------------------------------------
    # Load impact analysis
    # --------------------------------------

    impact = load_impact()

    if impact is None:
        return

    # --------------------------------------
    # Support both impact report formats
    # --------------------------------------

    if isinstance(impact, list):

        issues = impact

    elif isinstance(impact, dict):

        issues = impact.get(
            "issues",
            impact.get("repairs", [])
        )

    else:

        print("[ERROR] Invalid impact report format.")
        return

    if not isinstance(issues, list):

        print("[ERROR] Impact report issues field is not a list.")
        return

    # --------------------------------------
    # Create repair plan
    # --------------------------------------

    repair_plan = []

    print(f"Problems detected: {len(issues)}")
    print()

    # --------------------------------------
    # Create repair plans
    # --------------------------------------

    for issue in issues:

        if not isinstance(issue, dict):

            print("[WARNING] Skipping invalid issue entry.")
            print()

            continue

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

    # --------------------------------------
    # Save repair plan
    # --------------------------------------

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
                "project_status": "ISSUES_DETECTED",
                "repairs": repair_plan
            },
            file,
            indent=2
        )

    print(f"Repair plan saved: {REPAIR_FILE}")


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
