from pathlib import Path
import json

# ==========================================
# EAST SMP AI PRE-FIX IMPACT ANALYZER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPAIR_PLAN = PROJECT_ROOT / "reports" / "repair-plan.json"
IMPACT_REPORT = PROJECT_ROOT / "reports" / "impact.json"
DEPENDENCY_REPORT = PROJECT_ROOT / "reports" / "dependencies.json"
PREFIX_REPORT = PROJECT_ROOT / "reports" / "prefix.json"


def load_json(path):
    """Load a JSON file safely."""

    if not path.exists():
        print(f"[WARNING] File not found: {path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        print(f"[ERROR] Invalid JSON: {path}")
        print(error)
        return None

    except OSError as error:
        print(f"[ERROR] Could not read: {path}")
        print(error)
        return None


def get_repair_list(data):
    """Get repair entries from the repair plan."""

    if not isinstance(data, dict):
        return []

    repairs = data.get("repairs", [])

    if not isinstance(repairs, list):
        return []

    return repairs


def normalize_text(value):
    """Convert a value into searchable text."""

    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(str(item) for item in value)

    if isinstance(value, dict):
        return " ".join(
            f"{key} {value}"
            for key, value in value.items()
        )

    return str(value)


def analyze_repair(repair, dependency_data, impact_data):
    """Analyze the possible effects of one proposed repair."""

    issue = repair.get("issue", "Unknown issue")
    priority = repair.get("priority", "UNKNOWN")
    status = repair.get("status", "UNKNOWN")
    problem = repair.get("problem", "")

    automatic_allowed = bool(
        repair.get("automatic_modification", False)
    )

    proposed_action = repair.get(
        "proposed_action",
        []
    )

    safety_reason = repair.get(
        "safety_reason",
        ""
    )

    text = normalize_text(repair).lower()

    affected_files = []
    risks = []
    dependencies = []

    # ------------------------------------------
    # Identify likely affected areas
    # ------------------------------------------

    if "404" in text or "route" in text or "navigation" in text:
        affected_files.extend([
            "src/pages",
            "src/layouts",
            "src/components",
            "src/scripts",
            "public",
            "astro.config.mjs"
        ])

    if "speed" in text or "performance" in text:
        affected_files.extend([
            "src/pages",
            "src/components",
            "src/scripts",
            "src/styles",
            "public"
        ])

    # Remove duplicates
    affected_files = list(dict.fromkeys(affected_files))

    # ------------------------------------------
    # Dependency analysis
    # ------------------------------------------

    if dependency_data:

        dependency_text = normalize_text(
            dependency_data
        ).lower()

        if "layout.astro" in dependency_text:
            if (
                "route" in text
                or "404" in text
                or "navigation" in text
            ):
                dependencies.append(
                    "src/layouts/layout.astro"
                )

        if "siteinfo" in dependency_text:
            dependencies.append(
                "src/data/siteInfo.js"
            )

        if "styles.css" in dependency_text:
            if "speed" in text:
                dependencies.append(
                    "src/styles/styles.css"
                )

    # ------------------------------------------
    # Impact analysis
    # ------------------------------------------

    if impact_data:

        impact_text = normalize_text(
            impact_data
        ).lower()

        if "risk" in impact_text:
            risks.append(
                "Existing impact analysis identified potential dependent changes."
            )

    # ------------------------------------------
    # Issue-specific risks
    # ------------------------------------------

    if "404" in text:

        risks.extend([
            "Changing the wrong route could break navigation.",
            "Changing layout links could create additional broken links.",
            "Changing Astro routing could affect multiple pages.",
            "The development server may be serving a different route than expected."
        ])

    if "speed" in text:

        risks.extend([
            "The reported speed is already excellent.",
            "Changing website assets may provide no real improvement.",
            "Changing scripts or CSS could introduce regressions.",
            "The scanner's speed-test logic may be the actual problem."
        ])

    # Remove duplicate risks
    risks = list(dict.fromkeys(risks))

    # ------------------------------------------
    # Safety decision
    # ------------------------------------------

    blockers = []

    if not automatic_allowed:
        blockers.append(
            "Repair plan does not explicitly allow automatic modification."
        )

    if priority.upper() == "HIGH":
        blockers.append(
            "Issue is HIGH priority and requires additional verification."
        )

    if not affected_files:
        blockers.append(
            "No affected files could be confidently identified."
        )

    if not dependencies:
        blockers.append(
            "No verified file dependencies were established."
        )

    if status.upper() != "APPROVED":
        blockers.append(
            f"Repair status is {status}, not APPROVED."
        )

    # ------------------------------------------
    # Determine final decision
    # ------------------------------------------

    if blockers:
        decision = "BLOCKED"
    else:
        decision = "SAFE_TO_PROCEED"

    return {
        "issue": issue,
        "priority": priority,
        "status": status,
        "problem": problem,
        "proposed_action": proposed_action,
        "automatic_modification_allowed": automatic_allowed,
        "affected_files": affected_files,
        "dependencies": dependencies,
        "risks": risks,
        "blockers": blockers,
        "safety_decision": decision,
        "safety_reason": safety_reason
    }


def main():

    print()
    print("==========================================")
    print(" EAST SMP AI PRE-FIX IMPACT ANALYZER")
    print("==========================================")
    print()

    repair_data = load_json(REPAIR_PLAN)

    if repair_data is None:
        print("[FINAL SAFETY DECISION] BLOCKED")
        return

    impact_data = load_json(IMPACT_REPORT)
    dependency_data = load_json(DEPENDENCY_REPORT)

    repairs = get_repair_list(repair_data)

    print(f"Problems analyzed: {len(repairs)}")
    print()

    results = []

    for repair in repairs:

        result = analyze_repair(
            repair,
            dependency_data,
            impact_data
        )

        results.append(result)

        print("------------------------------------------")
        print()
        print(f"[ISSUE] {result['issue']}")
        print(f"[PRIORITY] {result['priority']}")
        print(f"[STATUS] {result['status']}")
        print()

        print("[AFFECTED FILES]")

        for file in result["affected_files"]:
            print(f"- {file}")

        print()

        print("[DEPENDENCIES]")

        if result["dependencies"]:
            for dependency in result["dependencies"]:
                print(f"- {dependency}")
        else:
            print("- None verified")

        print()

        print("[POTENTIAL RISKS]")

        for risk in result["risks"]:
            print(f"- {risk}")

        print()

        print("[SAFETY BLOCKERS]")

        if result["blockers"]:
            for blocker in result["blockers"]:
                print(f"- {blocker}")
        else:
            print("- None")

        print()

        print(
            f"[PRE-FIX DECISION] "
            f"{result['safety_decision']}"
        )

        print()

    # ------------------------------------------
    # Global safety decision
    # ------------------------------------------

    if not results:
        final_decision = "BLOCKED"

    elif any(
        result["safety_decision"] == "BLOCKED"
        for result in results
    ):
        final_decision = "BLOCKED"

    else:
        final_decision = "SAFE_TO_PROCEED"

    report = {
        "project": "East SMP Website 2.0",
        "repair_plan": str(REPAIR_PLAN),
        "problems_analyzed": len(results),
        "automatic_modification_authorized": (
            final_decision == "SAFE_TO_PROCEED"
        ),
        "final_safety_decision": final_decision,
        "repairs": results
    }

    PREFIX_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with PREFIX_REPORT.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=2
        )

    print("==========================================")
    print()
    print(
        f"Pre-fix report saved: {PREFIX_REPORT}"
    )
    print()
    print(
        f"[FINAL SAFETY DECISION] {final_decision}"
    )
    print()

    if final_decision == "BLOCKED":
        print(
            "[SAFETY] No automatic project modifications "
            "are permitted."
        )
    else:
        print(
            "[SAFETY] All pre-fix checks passed."
        )

    print()


if __name__ == "__main__":
    main()

