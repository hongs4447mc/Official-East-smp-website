from pathlib import Path
import subprocess
import sys
import json
from datetime import datetime


# ==========================================
# EAST SMP AI MASTER ORCHESTRATOR
# ==========================================
#
# Runs the complete AI safety pipeline.
#
# IMPORTANT:
# - Does NOT directly modify project files.
# - Repair engine remains in DRY-RUN mode.
# - Rollback remains PREVIEW-ONLY.
# - Verification must pass before the
#   operation is considered successful.
#
# ==========================================


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_ROOT / "ai"
REPORTS_DIR = PROJECT_ROOT / "reports"

ORCHESTRATOR_REPORT = (
    REPORTS_DIR / "orchestrator.json"
)


# ==========================================
# PIPELINE
# ==========================================

PIPELINE = [
    {
        "name": "Project Scanner",
        "file": "scanner.py",
        "required": True
    },
    {
        "name": "AI Analyzer",
        "file": "analyzer.py",
        "required": True
    },
    {
        "name": "Dependency Analyzer",
        "file": "dependency.py",
        "required": True
    },
    {
        "name": "Impact Analyzer",
        "file": "impact.py",
        "required": True
    },
    {
        "name": "Repair Planner",
        "file": "repair.py",
        "required": True
    },
    {
        "name": "Pre-Fix Impact Analyzer",
        "file": "prefix.py",
        "required": True
    },
    {
        "name": "Safety Gate",
        "file": "safety.py",
        "required": True
    },
    {
        "name": "Backup System",
        "file": "backup.py",
        "required": True
    },
    {
        "name": "Repair Engine",
        "file": "repair_engine.py",
        "required": True
    },
    {
        "name": "Verification",
        "file": "verify.py",
        "required": True
    },
    {
        "name": "History Logger",
        "file": "history.py",
        "required": True
    },
    {
        "name": "Rollback Preview",
        "file": "rollback.py",
        "required": True
    }
]


# ==========================================
# RUN SCRIPT
# ==========================================

def run_script(script):

    script_name = script["name"]
    script_file = AI_DIR / script["file"]

    print()
    print("==========================================")
    print(f"[AI PIPELINE] {script_name}")
    print("==========================================")
    print()

    if not script_file.exists():

        print(
            f"[ERROR] Missing script: "
            f"{script_file}"
        )

        return {
            "name": script_name,
            "file": script["file"],
            "status": "MISSING",
            "return_code": None
        }

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(script_file)
            ],
            cwd=PROJECT_ROOT,
            text=True
        )

        if result.returncode == 0:

            print()
            print(
                f"[PASS] {script_name} completed."
            )

            return {
                "name": script_name,
                "file": script["file"],
                "status": "PASSED",
                "return_code": 0
            }

        print()
        print(
            f"[FAIL] {script_name} "
            f"returned code "
            f"{result.returncode}."
        )

        return {
            "name": script_name,
            "file": script["file"],
            "status": "FAILED",
            "return_code": result.returncode
        }

    except OSError as error:

        print()
        print(
            f"[ERROR] Could not run "
            f"{script_name}."
        )

        print(error)

        return {
            "name": script_name,
            "file": script["file"],
            "status": "ERROR",
            "return_code": None,
            "error": str(error)
        }


# ==========================================
# LOAD VERIFICATION REPORT
# ==========================================

def check_verification():

    verification_file = (
        REPORTS_DIR / "verification.json"
    )

    if not verification_file.exists():

        return False

    try:

        with verification_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return False

    # Support several verification
    # report formats.

    if data.get("passed") is True:
        return True

    if data.get(
        "verification_passed"
    ) is True:

        return True

    status = str(
        data.get(
            "status",
            ""
        )
    ).upper()

    if status == "PASSED":
        return True

    final_status = str(
        data.get(
            "final_verification",
            ""
        )
    ).upper()

    if final_status == "PASSED":
        return True

    return False


# ==========================================
# LOAD SAFETY REPORT
# ==========================================

def check_safety():

    safety_file = (
        REPORTS_DIR / "safety.json"
    )

    if not safety_file.exists():

        return False

    try:

        with safety_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return False

    # A "no repair needed" state is safe.

    if data.get(
        "automatic_modification_allowed"
    ) is False:

        repairs = data.get(
            "repairs",
            0
        )

        if repairs == 0:

            return True

    if data.get(
        "overall_safe_to_modify"
    ) is True:

        return True

    return False


# ==========================================
# MAIN
# ==========================================

def main():

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    start_time = datetime.now()

    print()
    print("==========================================")
    print(" EAST SMP AI MASTER ORCHESTRATOR")
    print("==========================================")
    print()

    print(
        "[MODE] FULL SAFETY PIPELINE"
    )

    print(
        "[SAFETY] Automatic modification: DISABLED"
    )

    print(
        "[SAFETY] Repair engine: DRY RUN"
    )

    print(
        "[SAFETY] Rollback: PREVIEW ONLY"
    )

    print()

    results = []

    pipeline_failed = False

    # ======================================
    # RUN PIPELINE
    # ======================================

    for script in PIPELINE:

        result = run_script(
            script
        )

        results.append(
            result
        )

        if (
            result["status"] != "PASSED"
            and script["required"]
        ):

            pipeline_failed = True

            print()
            print(
                "[PIPELINE] Required step failed."
            )

            print(
                "[SAFETY] Stopping pipeline."
            )

            break

    # ======================================
    # CHECK FINAL STATE
    # ======================================

    verification_passed = (
        check_verification()
    )

    safety_passed = (
        check_safety()
    )

    # ======================================
    # FINAL DECISION
    # ======================================

    if pipeline_failed:

        final_status = "FAILED"

    elif not verification_passed:

        final_status = "VERIFICATION_FAILED"

    else:

        final_status = "PASSED"

    end_time = datetime.now()

    # ======================================
    # REPORT
    # ======================================

    report = {

        "project":
            "East SMP",

        "started":
            start_time.isoformat(),

        "finished":
            end_time.isoformat(),

        "pipeline_steps":
            len(results),

        "pipeline_total":
            len(PIPELINE),

        "verification_passed":
            verification_passed,

        "safety_passed":
            safety_passed,

        "automatic_modification":
            False,

        "repair_engine_mode":
            "DRY_RUN",

        "rollback_mode":
            "PREVIEW_ONLY",

        "files_modified":
            0,

        "final_status":
            final_status,

        "steps":
            results
    }

    with ORCHESTRATOR_REPORT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    # ======================================
    # FINAL OUTPUT
    # ======================================

    print()
    print("==========================================")
    print(" FINAL AI PIPELINE RESULT")
    print("==========================================")
    print()

    print(
        f"Pipeline steps: "
        f"{len(results)}/{len(PIPELINE)}"
    )

    print(
        f"Verification: "
        f"{'PASSED' if verification_passed else 'FAILED'}"
    )

    print(
        f"Safety gate: "
        f"{'PASSED' if safety_passed else 'BLOCKED'}"
    )

    print(
        "Automatic modification: DISABLED"
    )

    print(
        "Files modified: 0"
    )

    print()

    if final_status == "PASSED":

        print(
            "[FINAL AI DECISION] PASSED"
        )

        print(
            "[SAFETY] Project verification successful."
        )

        print(
            "[SAFETY] No automatic modifications occurred."
        )

    else:

        print(
            "[FINAL AI DECISION] FAILED"
        )

        print(
            "[SAFETY] The project should not be "
            "automatically modified."
        )

    print()

    print(
        f"Orchestrator report saved: "
        f"{ORCHESTRATOR_REPORT}"
    )

    print()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

