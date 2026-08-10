from pathlib import Path
import json
from datetime import datetime

# ==========================================
# EAST SMP AI REPAIR ENGINE
# DRY-RUN / NO FILE MODIFICATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = PROJECT_ROOT / "reports"

REPAIR_FILE = REPORTS_DIR / "repair-plan.json"
SAFETY_FILE = REPORTS_DIR / "safety.json"
DEPENDENCY_FILE = REPORTS_DIR / "dependencies.json"
PREFIX_FILE = REPORTS_DIR / "prefix.json"

ENGINE_REPORT = REPORTS_DIR / "repair-engine.json"


# ==========================================
# LOAD JSON
# ==========================================

def load_json(path, name):

    if not path.exists():

        print(f"[ERROR] {name} was not found.")
        print(f"Expected: {path}")

        return None

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError as error:

        print(f"[ERROR] {name} contains invalid JSON.")
        print(error)

        return None

    except OSError as error:

        print(f"[ERROR] Could not read {name}.")
        print(error)

        return None


# ==========================================
# CHECK PROJECT FILE
# ==========================================

def file_exists(relative_path):

    path = PROJECT_ROOT / relative_path

    return path.exists()


# ==========================================
# DETERMINE REPAIR TYPE
# ==========================================

def determine_repair_type(issue):

    name = issue.get(
        "issue",
        "Unknown issue"
    )

    if name == "Console Error Detector":

        return "ROUTE_INVESTIGATION"

    if name == "Load Speed Rating":

        return "SCANNER_LOGIC_INVESTIGATION"

    return "UNKNOWN"


# ==========================================
# CREATE DRY-RUN REPAIR
# ==========================================

def create_dry_run_repair(
    repair,
    dependency_data,
    prefix_data
):

    issue = repair.get(
        "issue",
        "Unknown issue"
    )

    priority = repair.get(
        "priority",
        "UNKNOWN"
    )

    problem = repair.get(
        "problem",
        ""
    )

    repair_type = determine_repair_type(
        repair
    )

    affected_files = repair.get(
        "affected_files",
        []
    )

    dependencies = []

    dependency_results = dependency_data.get(
        "dependencies",
        {}
    )

    for file in affected_files:

        dependency_info = dependency_results.get(
            file,
            {}
        )

        if dependency_info:

            dependencies.append(
                dependency_info
            )

    prefix_results = []

    if isinstance(prefix_data, dict):

        prefix_results = prefix_data.get(
            "results",
            []
        )

    # --------------------------------------
    # CONSOLE / ROUTE ISSUE
    # --------------------------------------

    if repair_type == "ROUTE_INVESTIGATION":

        proposed_actions = [

            "Verify the development server base path.",

            "Verify astro.config.mjs.",

            "Verify src/pages/index.astro exists.",

            "Verify the configured base URL.",

            "Check navigation links.",

            "Check layout links.",

            "Check whether localhost:4321/ is the correct test URL.",

            "Do not modify routing automatically."

        ]

    # --------------------------------------
    # SPEED ISSUE
    # --------------------------------------

    elif repair_type == "SCANNER_LOGIC_INVESTIGATION":

        proposed_actions = [

            "Inspect the scanner speed-test logic.",

            "Verify the reported response time.",

            "Verify the pass/fail threshold.",

            "Compare the measured value with the displayed rating.",

            "Do not modify website assets.",

            "Do not change CSS or JavaScript for this issue."

        ]

    # --------------------------------------
    # UNKNOWN
    # --------------------------------------

    else:

        proposed_actions = [

            "Investigate the issue.",

            "Identify the exact affected files.",

            "Analyze dependencies.",

            "Perform pre-fix impact analysis.",

            "Do not modify files automatically."

        ]

    return {

        "issue": issue,

        "priority": priority,

        "repair_type": repair_type,

        "problem": problem,

        "affected_files": affected_files,

        "dependencies_checked": dependencies,

        "prefix_analysis_available": bool(
            prefix_results
        ),

        "proposed_actions": proposed_actions,

        "mode": "DRY_RUN",

        "files_modified": [],

        "modification_performed": False,

        "status": "PROPOSAL_ONLY"

    }


# ==========================================
# SAFETY CHECK
# ==========================================

def safety_allows_execution(safety_data):

    if not safety_data:
        return False

    return (
        safety_data.get(
            "overall_safe_to_modify",
            False
        )
        is True
        and
        safety_data.get(
            "automatic_modification_allowed",
            False
        )
        is True
    )


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI REPAIR ENGINE")
    print("==========================================")
    print()

    print("[MODE] DRY RUN")
    print("[SAFETY] NO FILES WILL BE MODIFIED.")
    print()

    # --------------------------------------
    # LOAD REPORTS
    # --------------------------------------

    repair_data = load_json(
        REPAIR_FILE,
        "repair-plan.json"
    )

    if repair_data is None:
        return

    safety_data = load_json(
        SAFETY_FILE,
        "safety.json"
    )

    if safety_data is None:
        return

    dependency_data = load_json(
        DEPENDENCY_FILE,
        "dependencies.json"
    )

    if dependency_data is None:
        return

    prefix_data = load_json(
        PREFIX_FILE,
        "prefix.json"
    )

    if prefix_data is None:

        print(
            "[WARNING] prefix.json was not found."
        )

        prefix_data = {}

    # --------------------------------------
    # SAFETY STATUS
    # --------------------------------------

    allowed = safety_allows_execution(
        safety_data
    )

    print(
        "[SAFETY] Automatic modification allowed:",
        allowed
    )

    if not allowed:

        print()
        print(
            "[SAFETY] Automatic repair execution "
            "is BLOCKED."
        )

        print(
            "[SAFETY] Continuing in DRY-RUN mode."
        )

    print()

    repairs = repair_data.get(
        "repairs",
        []
    )

    print(
        f"Repair proposals: {len(repairs)}"
    )

    print()

    results = []

    # --------------------------------------
    # PROCESS EVERY REPAIR
    # --------------------------------------

    for repair in repairs:

        result = create_dry_run_repair(
            repair,
            dependency_data,
            prefix_data
        )

        results.append(result)

        print(
            "------------------------------------------"
        )

        print(
            f"[ISSUE] {result['issue']}"
        )

        print(
            f"[PRIORITY] {result['priority']}"
        )

        print(
            f"[TYPE] {result['repair_type']}"
        )

        print(
            f"[STATUS] {result['status']}"
        )

        print()

        print(
            "[PROPOSED ACTIONS]"
        )

        for action in result[
            "proposed_actions"
        ]:

            print(
                f"- {action}"
            )

        print()

        print(
            "[FILES THAT WOULD BE MODIFIED]"
        )

        if result["affected_files"]:

            for file in result[
                "affected_files"
            ]:

                print(
                    f"- {file}"
                )

        else:

            print(
                "- NONE VERIFIED"
            )

        print()

        print(
            "[MODIFICATION]"
        )

        print(
            "No modification performed."
        )

    # --------------------------------------
    # FINAL DECISION
    # --------------------------------------

    print()
    print("==========================================")

    if not repairs:

        print(
            " NO REPAIRS REQUIRED"
        )

    else:

        print(
            " DRY-RUN COMPLETE"
        )

    print("==========================================")
    print()

    print(
        "[SAFETY] Files modified: 0"
    )

    print(
        "[SAFETY] Automatic modification:",
        "DISABLED"
    )

    # --------------------------------------
    # SAVE REPORT
    # --------------------------------------

    engine_report = {

        "timestamp":
            datetime.now().isoformat(),

        "mode":
            "DRY_RUN",

        "automatic_modification_allowed":
            False,

        "modification_performed":
            False,

        "files_modified":
            [],

        "repair_count":
            len(results),

        "repairs":
            results

    }

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with ENGINE_REPORT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            engine_report,
            file,
            indent=2
        )

    print(
        f"Repair engine report saved: "
        f"{ENGINE_REPORT}"
    )

    print()
    print(
        "[FINAL SAFETY DECISION] "
        "DRY-RUN ONLY"
    )

    print(
        "[SAFETY] No project files were modified."
    )


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()

