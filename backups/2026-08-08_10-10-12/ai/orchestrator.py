from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime

# ============================================================
# EAST SMP AI ORCHESTRATOR
# DEPENDENT REPAIR ANALYSIS + SAFETY PIPELINE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_ROOT / "ai"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORT_FILE = REPORTS_DIR / "orchestrator.json"

# ------------------------------------------------------------
# Pipeline configuration
# ------------------------------------------------------------

STEPS = [
    ("Scanner", "scanner.py"),
    ("Dependency Analyzer", "dependency.py"),
    ("Impact Analyzer", "impact.py"),
    ("Repair Planner", "repair.py"),
    ("Pre-Fix Impact Analyzer", "prefix.py"),
    ("Dependent-Fix Impact Analyzer", "dependent_impact.py"),
    ("Safety Gate", "safety.py"),
    ("Backup System", "backup.py"),
    ("Repair Engine", "repair_engine.py"),
    ("Verification", "verify.py"),
    ("History Logger", "history.py"),
    ("Rollback Preview", "rollback.py"),
]

# ------------------------------------------------------------
# Safety policy
# ------------------------------------------------------------

AUTOMATIC_MODIFICATION_ENABLED = False

MAX_DEPENDENT_DEPTH = 10

# A repair must satisfy ALL of these before execution.
REQUIRED_SAFETY_REPORTS = [
    "safety.json",
    "prefix.json",
    "dependent-impact.json",
    "backup.json",
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None


def save_json(path, data):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


# ============================================================
# RUN PYTHON PIPELINE STEP
# ============================================================

def run_step(name, filename):
    print()
    print("=" * 42)
    print(f"[AI PIPELINE] {name}")
    print("=" * 42)
    print()

    script = AI_DIR / filename

    if not script.exists():
        print(f"[FAIL] Missing pipeline script: {script}")

        return {
            "name": name,
            "script": filename,
            "passed": False,
            "error": "SCRIPT_NOT_FOUND",
        }

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(script),
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            text=True,
        )

        passed = result.returncode == 0

        if passed:
            print()
            print(f"[PASS] {name} completed.")
        else:
            print()
            print(f"[FAIL] {name} failed.")

        return {
            "name": name,
            "script": filename,
            "passed": passed,
            "return_code": result.returncode,
        }

    except OSError as error:
        print(f"[FAIL] Could not run {name}.")
        print(error)

        return {
            "name": name,
            "script": filename,
            "passed": False,
            "error": str(error),
        }


# ============================================================
# LOAD REPAIR PLAN
# ============================================================

def load_repairs():
    repair_file = REPORTS_DIR / "repair-plan.json"

    data = load_json(repair_file)

    if not data:
        return []

    repairs = data.get("repairs", [])

    if not isinstance(repairs, list):
        return []

    return repairs


# ============================================================
# GET AFFECTED FILES
# ============================================================

def get_affected_files(repair):
    files = repair.get("affected_files", [])

    if not isinstance(files, list):
        return []

    return [
        str(file)
        for file in files
        if isinstance(file, str)
    ]


# ============================================================
# LOAD DEPENDENCY GRAPH
# ============================================================

def load_dependencies():
    dependency_file = REPORTS_DIR / "dependencies.json"

    data = load_json(dependency_file)

    if not data:
        return {}

    return data


# ============================================================
# DEPENDENCY LOOKUP
# ============================================================

def find_dependents(file_path, dependency_data):
    """
    Find files that depend on the supplied file.

    Supports the dependency format produced by the
    East SMP dependency analyzer.
    """

    dependents = []

    dependencies = dependency_data.get(
        "dependencies",
        {}
    )

    if not isinstance(dependencies, dict):
        return dependents

    normalized_target = str(
        Path(file_path)
    ).replace("\\", "/")

    for dependency_file, information in dependencies.items():

        if not isinstance(information, dict):
            continue

        sources = information.get(
            "used_by",
            information.get(
                "dependents",
                information.get(
                    "references",
                    []
                )
            )
        )

        if not isinstance(sources, list):
            continue

        for source in sources:

            normalized_source = str(
                source
            ).replace("\\", "/")

            if normalized_source == normalized_target:
                dependents.append(
                    str(dependency_file)
                )

    return sorted(
        set(dependents)
    )


# ============================================================
# RECURSIVE DEPENDENT REPAIR DISCOVERY
# ============================================================

def discover_dependent_files(
    initial_files,
    dependency_data,
):
    """
    Recursively discover files that could be affected by
    the proposed repair set.

    This does NOT modify anything.
    """

    discovered = set()
    queue = []

    for file_path in initial_files:

        normalized = str(
            file_path
        ).replace("\\", "/")

        if normalized not in discovered:

            discovered.add(normalized)

            queue.append(
                (
                    normalized,
                    0
                )
            )

    while queue:

        current_file, depth = queue.pop(0)

        if depth >= MAX_DEPENDENT_DEPTH:
            continue

        dependents = find_dependents(
            current_file,
            dependency_data
        )

        for dependent in dependents:

            normalized = str(
                dependent
            ).replace("\\", "/")

            if normalized in discovered:
                continue

            discovered.add(normalized)

            queue.append(
                (
                    normalized,
                    depth + 1
                )
            )

    return sorted(discovered)


# ============================================================
# BUILD COMPLETE FIX SET
# ============================================================

def build_complete_fix_set(
    repairs,
    dependency_data,
):
    """
    Build the complete proposed change set.

    The original repairs are combined with every dependent
    file discovered recursively.
    """

    original_files = set()

    for repair in repairs:

        for file_path in get_affected_files(
            repair
        ):

            original_files.add(
                file_path.replace(
                    "\\",
                    "/"
                )
            )

    dependent_files = discover_dependent_files(
        sorted(original_files),
        dependency_data
    )

    all_files = sorted(
        set(original_files)
        | set(dependent_files)
    )

    return {
        "original_files": sorted(
            original_files
        ),

        "dependent_files": sorted(
            set(dependent_files)
            - set(original_files)
        ),

        "complete_fix_set": all_files,

        "dependency_depth_limit":
            MAX_DEPENDENT_DEPTH,
    }


# ============================================================
# ANALYZE SAFETY REPORTS
# ============================================================

def evaluate_safety_reports():
    results = {}

    for filename in REQUIRED_SAFETY_REPORTS:

        path = REPORTS_DIR / filename

        data = load_json(path)

        if data is None:

            results[filename] = {
                "exists": False,
                "passed": False,
            }

            continue

        results[filename] = {
            "exists": True,
            "passed": evaluate_report(
                filename,
                data
            ),
        }

    return results


# ============================================================
# INDIVIDUAL REPORT SAFETY
# ============================================================

def evaluate_report(filename, data):

    if filename == "safety.json":

        return (
            data.get(
                "automatic_modification_allowed",
                False
            )
            is True
            and
            data.get(
                "overall_safe_to_modify",
                False
            )
            is True
        )

    if filename == "prefix.json":

        return data.get(
            "overall_safe_to_modify",
            False
        ) is True

    if filename == "dependent-impact.json":

        return (
            data.get(
                "overall_safe",
                False
            )
            is True
        )

    if filename == "backup.json":

        return (
            data.get(
                "verified",
                False
            )
            is True
        )

    return False


# ============================================================
# COMPLETE REPAIR DECISION
# ============================================================

def determine_repair_permission(
    repairs,
    fix_set,
    safety_reports,
):
    reasons = []

    # --------------------------------------------------------
    # No repairs
    # --------------------------------------------------------

    if not repairs:

        return {
            "allowed": False,
            "reason": "NO_REPAIRS_REQUIRED",
            "reasons": [
                "The current repair plan contains no repairs."
            ],
        }

    # --------------------------------------------------------
    # Global modification lock
    # --------------------------------------------------------

    if not AUTOMATIC_MODIFICATION_ENABLED:

        reasons.append(
            "Automatic modification is disabled "
            "by the project safety policy."
        )

    # --------------------------------------------------------
    # Affected files
    # --------------------------------------------------------

    if not fix_set["complete_fix_set"]:

        reasons.append(
            "No verified affected files were identified."
        )

    # --------------------------------------------------------
    # Safety reports
    # --------------------------------------------------------

    for filename, result in safety_reports.items():

        if not result["exists"]:

            reasons.append(
                f"Required safety report is missing: "
                f"{filename}"
            )

        elif not result["passed"]:

            reasons.append(
                f"Required safety report did not approve "
                f"modification: {filename}"
            )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

    allowed = (
        len(reasons) == 0
    )

    return {
        "allowed": allowed,
        "reason": (
            "ALL_SAFETY_REQUIREMENTS_PASSED"
            if allowed
            else "SAFETY_REQUIREMENTS_NOT_MET"
        ),
        "reasons": reasons,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    started = timestamp()

    print()
    print("=" * 50)
    print(" EAST SMP AI ORCHESTRATOR")
    print(" DEPENDENT REPAIR SAFETY PIPELINE")
    print("=" * 50)
    print()

    print(
        "[SAFETY] Automatic modification:",
        "ENABLED"
        if AUTOMATIC_MODIFICATION_ENABLED
        else "DISABLED"
    )

    print(
        f"[SAFETY] Maximum dependent depth: "
        f"{MAX_DEPENDENT_DEPTH}"
    )

    step_results = []

    # ========================================================
    # STANDARD ANALYSIS PIPELINE
    # ========================================================

    for name, filename in STEPS:

        result = run_step(
            name,
            filename
        )

        step_results.append(result)

        if not result["passed"]:

            print()
            print(
                "[PIPELINE] A required step failed."
            )

            print(
                "[SAFETY] Pipeline execution stopped."
            )

            report = {
                "started": started,
                "completed": timestamp(),
                "pipeline_passed": False,
                "automatic_modification": (
                    AUTOMATIC_MODIFICATION_ENABLED
                ),
                "steps": step_results,
                "final_decision": "BLOCKED",
                "reason": "PIPELINE_STEP_FAILED",
            }

            save_json(
                REPORT_FILE,
                report
            )

            print()
            print(
                f"Orchestrator report saved: "
                f"{REPORT_FILE}"
            )

            return

    # ========================================================
    # DEPENDENT REPAIR ANALYSIS
    # ========================================================

    print()
    print("=" * 50)
    print("[AI PIPELINE] Complete Dependent Repair Analysis")
    print("=" * 50)
    print()

    repairs = load_repairs()

    dependency_data = load_dependencies()

    if dependency_data is None:

        print(
            "[FAIL] Dependency report could not be loaded."
        )

        report = {
            "started": started,
            "completed": timestamp(),
            "pipeline_passed": False,
            "final_decision": "BLOCKED",
            "reason": "DEPENDENCY_REPORT_MISSING",
            "steps": step_results,
        }

        save_json(
            REPORT_FILE,
            report
        )

        return

    fix_set = build_complete_fix_set(
        repairs,
        dependency_data
    )

    print(
        f"[REPAIRS] Original repairs: "
        f"{len(repairs)}"
    )

    print(
        f"[FILES] Original affected files: "
        f"{len(fix_set['original_files'])}"
    )

    print(
        f"[FILES] Dependent files discovered: "
        f"{len(fix_set['dependent_files'])}"
    )

    print(
        f"[FILES] Complete proposed fix set: "
        f"{len(fix_set['complete_fix_set'])}"
    )

    # --------------------------------------------------------
    # Display dependent files
    # --------------------------------------------------------

    if fix_set["dependent_files"]:

        print()
        print(
            "[DEPENDENT FILES]"
        )

        for file_path in fix_set[
            "dependent_files"
        ]:

            print(
                f"- {file_path}"
            )

    else:

        print()
        print(
            "[DEPENDENT FILES] None discovered."
        )

    # ========================================================
    # RECURSIVE SAFETY REQUIREMENT
    # ========================================================

    print()
    print(
        "[SAFETY] Evaluating complete proposed fix set..."
    )

    safety_reports = evaluate_safety_reports()

    permission = determine_repair_permission(
        repairs,
        fix_set,
        safety_reports
    )

    # ========================================================
    # FINAL DECISION
    # ========================================================

    print()
    print("=" * 50)

    if permission["allowed"]:

        print(
            "[FINAL REPAIR DECISION] APPROVED"
        )

        print(
            "[SAFETY] Complete repair set passed all "
            "required safety checks."
        )

    else:

        print(
            "[FINAL REPAIR DECISION] BLOCKED"
        )

        print(
            "[SAFETY] Complete repair set was NOT approved."
        )

        for reason in permission["reasons"]:

            print(
                f"- {reason}"
            )

    print("=" * 50)

    # ========================================================
    # IMPORTANT:
    # THIS ORCHESTRATOR DOES NOT MODIFY FILES.
    # ========================================================

    print()
    print(
        "[SAFETY] Orchestrator does not directly modify files."
    )

    print(
        "[SAFETY] Repair execution remains controlled by "
        "the repair engine."
    )

    # ========================================================
    # SAVE REPORT
    # ========================================================

    report = {
        "started": started,
        "completed": timestamp(),

        "project": "East SMP",

        "pipeline_passed": all(
            result["passed"]
            for result in step_results
        ),

        "automatic_modification": (
            AUTOMATIC_MODIFICATION_ENABLED
        ),

        "repairs": {
            "original_count": len(repairs),
            "original_files": fix_set[
                "original_files"
            ],
            "dependent_files": fix_set[
                "dependent_files"
            ],
            "complete_fix_set": fix_set[
                "complete_fix_set"
            ],
        },

        "dependent_analysis": {
            "recursive": True,
            "maximum_depth":
                MAX_DEPENDENT_DEPTH,
            "completed": True,
        },

        "safety_reports":
            safety_reports,

        "repair_permission":
            permission,

        "steps":
            step_results,

        "files_modified": 0,

        "final_decision": (
            "APPROVED"
            if permission["allowed"]
            else "BLOCKED"
        ),
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print(
        f"Orchestrator report saved: "
        f"{REPORT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

