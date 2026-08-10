from pathlib import Path
import json

# ==========================================
# EAST SMP AI SAFETY GATE
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPAIR_FILE = PROJECT_ROOT / "reports" / "repair-plan.json"
DEPENDENCY_FILE = PROJECT_ROOT / "reports" / "dependencies.json"
SAFETY_FILE = PROJECT_ROOT / "reports" / "safety.json"


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
# DETERMINE SAFETY
# ==========================================

def evaluate_repair(repair, dependencies):

    issue = repair.get(
        "issue",
        "Unknown issue"
    )

    priority = repair.get(
        "priority",
        "UNKNOWN"
    )

    automatic = repair.get(
        "automatic_modification",
        False
    )

    affected_files = repair.get(
        "affected_files",
        []
    )

    reasons = []

    # --------------------------------------
    # DEFAULT: BLOCK AUTOMATIC MODIFICATION
    # --------------------------------------

    safe = False

    # --------------------------------------
    # CHECK AUTOMATIC MODIFICATION FLAG
    # --------------------------------------

    if automatic is not True:

        reasons.append(
            "Repair plan does not explicitly allow automatic modification."
        )

    # --------------------------------------
    # HIGH PRIORITY ISSUES
    # --------------------------------------

    if priority == "HIGH":

        reasons.append(
            "Issue is HIGH priority and requires additional verification."
        )

    # --------------------------------------
    # UNKNOWN ISSUES
    # --------------------------------------

    if issue == "Unknown issue":

        reasons.append(
            "Issue could not be identified."
        )

    # --------------------------------------
    # CHECK AFFECTED FILES
    # --------------------------------------

    if not affected_files:

        reasons.append(
            "No verified affected files were provided."
        )

    # --------------------------------------
    # CHECK DEPENDENCIES
    # --------------------------------------

    high_risk_files = []

    risks = dependencies.get(
        "risks",
        {}
    )

    for file in affected_files:

        risk = risks.get(
            file,
            {}
        )

        if risk.get("level") == "HIGH":

            high_risk_files.append(file)

    if high_risk_files:

        reasons.append(
            "HIGH-risk dependencies detected: "
            + ", ".join(high_risk_files)
        )

    # --------------------------------------
    # CURRENT PROJECT REPAIR PLANNER
    # --------------------------------------
    #
    # Our current repair system deliberately
    # keeps automatic modification disabled.
    #
    # Therefore the safety gate must remain
    # locked until a later stage explicitly
    # enables controlled modifications.
    # --------------------------------------

    reasons.append(
        "Automatic modification is currently disabled by the project safety policy."
    )

    return {
        "issue": issue,
        "priority": priority,
        "safe_to_modify": safe,
        "automatic_modification_allowed": False,
        "reasons": reasons
    }


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI SAFETY GATE")
    print("==========================================")
    print()

    repair_data = load_json(
        REPAIR_FILE,
        "repair-plan.json"
    )

    if repair_data is None:
        return

    dependency_data = load_json(
        DEPENDENCY_FILE,
        "dependencies.json"
    )

    if dependency_data is None:
        return

    repairs = repair_data.get(
        "repairs",
        []
    )

    results = []

    print(
        f"Repairs evaluated: {len(repairs)}"
    )

    print()

    # ======================================
    # EVALUATE EVERY REPAIR
    # ======================================

    for repair in repairs:

        result = evaluate_repair(
            repair,
            dependency_data
        )

        results.append(result)

        print(
            f"[ISSUE] {result['issue']}"
        )

        print(
            f"[PRIORITY] {result['priority']}"
        )

        if result["safe_to_modify"]:

            print(
                "[SAFETY] SAFE"
            )

        else:

            print(
                "[SAFETY] BLOCKED"
            )

        print()

        print(
            "[REASONS]"
        )

        for reason in result["reasons"]:

            print(
                f"- {reason}"
            )

        print()
        print("------------------------------------------")
        print()

    # ======================================
    # OVERALL SAFETY
    # ======================================

    blocked = sum(
        1
        for result in results
        if not result["safe_to_modify"]
    )

    approved = sum(
        1
        for result in results
        if result["safe_to_modify"]
    )

    overall_safe = (
        len(results) > 0
        and blocked == 0
        and approved > 0
    )

    safety_report = {
        "automatic_modification_allowed": False,
        "overall_safe_to_modify": overall_safe,
        "repairs_evaluated": len(results),
        "repairs_approved": approved,
        "repairs_blocked": blocked,
        "results": results
    }

    # ======================================
    # SAVE REPORT
    # ======================================

    SAFETY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with SAFETY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            safety_report,
            file,
            indent=2
        )

    print(
        f"Safety report saved: {SAFETY_FILE}"
    )

    print()

    if overall_safe:

        print(
            "[FINAL SAFETY DECISION] SAFE"
        )

    else:

        print(
            "[FINAL SAFETY DECISION] BLOCKED"
        )

        print(
            "No automatic project modifications are permitted."
        )


if __name__ == "__main__":
    main()

