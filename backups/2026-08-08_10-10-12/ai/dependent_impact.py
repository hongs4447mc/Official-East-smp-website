from pathlib import Path
import json

# ==========================================
# EAST SMP AI DEPENDENT-FIX IMPACT ANALYZER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPAIR_FILE = PROJECT_ROOT / "reports" / "repair-plan.json"
DEPENDENCY_FILE = PROJECT_ROOT / "reports" / "dependencies.json"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "dependent-impact.json"


# ==========================================
# LOAD JSON
# ==========================================

def load_json(path, name):
    if not path.exists():
        print(f"[ERROR] {name} was not found.")
        print(f"Expected: {path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
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
# NORMALIZE PATH
# ==========================================

def normalize_path(path):
    if not path:
        return ""

    return str(path).replace("\\", "/").strip()


# ==========================================
# BUILD DEPENDENCY GRAPH
# ==========================================

def build_dependency_graph(dependencies):
    graph = {}

    risks = dependencies.get("risks", {})

    for file_name, information in risks.items():

        file_name = normalize_path(file_name)

        if not file_name:
            continue

        graph.setdefault(
            file_name,
            {
                "dependents": [],
                "risk": "UNKNOWN"
            }
        )

        graph[file_name]["risk"] = information.get(
            "level",
            "UNKNOWN"
        )

        dependents = information.get(
            "dependents",
            []
        )

        if isinstance(dependents, list):
            graph[file_name]["dependents"].extend(
                normalize_path(item)
                for item in dependents
                if item
            )

    # Some dependency analyzers store relationships
    # directly as lists instead of inside "risks".
    dependency_list = dependencies.get(
        "dependencies",
        {}
    )

    if isinstance(dependency_list, dict):

        for file_name, dependents in dependency_list.items():

            file_name = normalize_path(file_name)

            graph.setdefault(
                file_name,
                {
                    "dependents": [],
                    "risk": "UNKNOWN"
                }
            )

            if isinstance(dependents, list):

                graph[file_name]["dependents"].extend(
                    normalize_path(item)
                    for item in dependents
                    if item
                )

    return graph


# ==========================================
# FIND DEPENDENTS RECURSIVELY
# ==========================================

def find_recursive_dependents(
    starting_files,
    graph
):
    discovered = set()
    queue = []

    for file_name in starting_files:

        file_name = normalize_path(file_name)

        if file_name:
            queue.append(file_name)

    while queue:

        current = queue.pop(0)

        if current in discovered:
            continue

        discovered.add(current)

        node = graph.get(
            current,
            {}
        )

        dependents = node.get(
            "dependents",
            []
        )

        for dependent in dependents:

            dependent = normalize_path(
                dependent
            )

            if (
                dependent
                and dependent not in discovered
            ):
                queue.append(dependent)

    return discovered


# ==========================================
# DETERMINE RISK
# ==========================================

def determine_risk(files, graph):

    highest = "LOW"

    ranking = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "UNKNOWN": 4
    }

    for file_name in files:

        node = graph.get(
            file_name,
            {}
        )

        risk = node.get(
            "risk",
            "UNKNOWN"
        )

        if ranking.get(
            risk,
            4
        ) > ranking.get(
            highest,
            4
        ):
            highest = risk

    return highest


# ==========================================
# ANALYZE REPAIR
# ==========================================

def analyze_repair(
    repair,
    graph
):

    issue = repair.get(
        "issue",
        "Unknown issue"
    )

    priority = repair.get(
        "priority",
        "UNKNOWN"
    )

    affected_files = repair.get(
        "affected_files",
        []
    )

    affected_files = [
        normalize_path(file_name)
        for file_name in affected_files
        if file_name
    ]

    # --------------------------------------
    # No files = cannot safely analyze
    # --------------------------------------

    if not affected_files:

        return {
            "issue": issue,
            "priority": priority,
            "status": "BLOCKED",
            "safe_to_continue": False,
            "directly_affected_files": [],
            "dependent_files": [],
            "complete_fix_set": [],
            "risk": "UNKNOWN",
            "related_issues": [],
            "reasons": [
                "No verified affected files were provided.",
                "The complete dependent fix set cannot be determined."
            ]
        }

    # --------------------------------------
    # Recursive dependency analysis
    # --------------------------------------

    complete_set = find_recursive_dependents(
        affected_files,
        graph
    )

    dependent_files = (
        complete_set
        - set(affected_files)
    )

    risk = determine_risk(
        complete_set,
        graph
    )

    reasons = []

    safe = True

    # --------------------------------------
    # HIGH / UNKNOWN risk
    # --------------------------------------

    if risk == "HIGH":

        safe = False

        reasons.append(
            "HIGH-risk files are included in the dependent fix set."
        )

    if risk == "UNKNOWN":

        safe = False

        reasons.append(
            "One or more dependencies have UNKNOWN risk."
        )

    # --------------------------------------
    # Recursive dependency discovered
    # --------------------------------------

    if dependent_files:

        reasons.append(
            "Dependent files were discovered recursively."
        )

    else:

        reasons.append(
            "No additional dependent files were discovered."
        )

    # --------------------------------------
    # Automatic modification remains blocked
    # --------------------------------------

    safe = False

    reasons.append(
        "Automatic modification remains disabled by project safety policy."
    )

    return {
        "issue": issue,
        "priority": priority,
        "status": "ANALYZED",
        "safe_to_continue": safe,
        "directly_affected_files": sorted(
            affected_files
        ),
        "dependent_files": sorted(
            dependent_files
        ),
        "complete_fix_set": sorted(
            complete_set
        ),
        "risk": risk,
        "related_issues": [],
        "reasons": reasons
    }


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI DEPENDENT-FIX IMPACT ANALYZER")
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

    graph = build_dependency_graph(
        dependency_data
    )

    print(
        f"Repairs analyzed: {len(repairs)}"
    )

    print()

    results = []

    for repair in repairs:

        result = analyze_repair(
            repair,
            graph
        )

        results.append(result)

        print(
            f"[ISSUE] {result['issue']}"
        )

        print(
            f"[PRIORITY] {result['priority']}"
        )

        print(
            f"[RISK] {result['risk']}"
        )

        print(
            f"[DIRECT FILES] "
            f"{len(result['directly_affected_files'])}"
        )

        print(
            f"[DEPENDENT FILES] "
            f"{len(result['dependent_files'])}"
        )

        print(
            f"[COMPLETE FIX SET] "
            f"{len(result['complete_fix_set'])}"
        )

        print()

        print("[REASONS]")

        for reason in result["reasons"]:
            print(
                f"- {reason}"
            )

        print()
        print("------------------------------------------")
        print()

    # ======================================
    # OVERALL DECISION
    # ======================================

    blocked = sum(
        1
        for result in results
        if not result["safe_to_continue"]
    )

    analyzed = len(results)

    # Automatic modification is ALWAYS disabled.
    automatic_allowed = False

    overall_safe = (
        analyzed > 0
        and blocked == 0
        and automatic_allowed
    )

    report = {
        "automatic_modification_allowed": False,
        "overall_safe_to_continue": overall_safe,
        "repairs_analyzed": analyzed,
        "repairs_blocked": blocked,
        "results": results
    }

    # ======================================
    # SAVE REPORT
    # ======================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    print(
        f"Dependent impact report saved: "
        f"{OUTPUT_FILE}"
    )

    print()

    print(
        "[FINAL SAFETY DECISION] BLOCKED"
    )

    print(
        "[SAFETY] Automatic project modifications "
        "remain disabled."
    )

    print(
        "[SAFETY] This analyzer only determines "
        "the potential dependent impact."
    )


if __name__ == "__main__":
    main()

