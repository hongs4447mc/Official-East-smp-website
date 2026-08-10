"""
EAST SMP AI ORCHESTRATOR
Dependent Repair Upgrade

Pipeline:
    Scanner
        ↓
    Dependency Analyzer
        ↓
    Impact Analyzer
        ↓
    Repair Planner
        ↓
    Pre-Fix Impact Analyzer
        ↓
    Dependent-Fix Discovery
        ↓
    Recursive Dependent Analysis
        ↓
    Complete Fix-Set Reanalysis
        ↓
    Safety Gate
        ↓
    Verified Backup
        ↓
    Repair Engine
        ↓
    Post-Change Verification
        ↓
    Rollback on Verification Failure
        ↓
    History Logger

IMPORTANT:
- This orchestrator does NOT directly modify project files.
- Automatic modification remains disabled.
- A repair is only eligible after the COMPLETE proposed fix set passes analysis.
- Backups/reports/generated files are excluded from dependency repair propagation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / "ai"
REPORTS_DIR = ROOT / "reports"
BACKUPS_DIR = ROOT / "backups"

AUTOMATIC_MODIFICATION = False

MAX_DEPENDENT_DEPTH = 10

# These directories/files must NEVER become repair targets
# simply because they appear in dependency reports.
IGNORED_ROOTS = {
    "backups",
    "reports",
    "dist",
    "node_modules",
    ".git",
    ".astro",
    ".cache",
    "__pycache__",
}

IGNORED_FILES = {
    "scanner.json",
    "dependencies.json",
    "impact.json",
    "repair-plan.json",
    "prefix.json",
    "dependent-impact.json",
    "safety.json",
    "backup.json",
    "repair-engine.json",
    "verification.json",
    "ai-history.json",
    "rollback.json",
    "orchestrator.json",
}


# ============================================================
# REPORT HELPERS
# ============================================================

def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def report_path(name: str) -> Path:
    return REPORTS_DIR / name


def load_json(name: str, default: Any = None) -> Any:
    path = report_path(name)

    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[WARN] Could not read {name}: {exc}")
        return default


def save_json(name: str, data: Any) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    path = report_path(name)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ============================================================
# PATH NORMALIZATION
# ============================================================

def normalize_path(value: str | Path) -> str:
    """
    Normalize a project path.

    The dependency reports can contain:
        backups/...
        ./src/...
        src\\...
        src/...

    Convert them into a consistent project-relative form.
    """

    text = str(value).strip().strip('"').strip("'")

    text = text.replace("\\", "/")

    while text.startswith("./"):
        text = text[2:]

    # Convert absolute project paths to relative paths.
    try:
        candidate = Path(text)

        if candidate.is_absolute():
            text = candidate.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        pass

    return text


def is_generated_or_backup(path: str) -> bool:
    normalized = normalize_path(path)

    if not normalized:
        return True

    parts = normalized.split("/")

    if any(part in IGNORED_ROOTS for part in parts):
        return True

    if parts[-1] in IGNORED_FILES:
        return True

    return False


def is_real_project_file(path: str) -> bool:
    normalized = normalize_path(path)

    if is_generated_or_backup(normalized):
        return False

    return (ROOT / normalized).exists()


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_step(
    name: str,
    script: str,
    *,
    required: bool = True,
) -> dict[str, Any]:

    print()
    print("=" * 58)
    print(f"[ORCHESTRATOR] {name}")
    print("=" * 58)

    script_path = AI_DIR / script

    if not script_path.exists():
        message = f"Missing script: {script_path}"

        print(f"[FAIL] {message}")

        result = {
            "name": name,
            "script": script,
            "passed": False,
            "return_code": -1,
            "error": message,
        }

        if required:
            raise RuntimeError(message)

        return result

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(ROOT),
            text=True,
        )

        passed = completed.returncode == 0

        print(
            f"[{'PASS' if passed else 'FAIL'}] "
            f"{name} completed."
        )

        result = {
            "name": name,
            "script": script,
            "passed": passed,
            "return_code": completed.returncode,
        }

        if required and not passed:
            raise RuntimeError(
                f"{name} failed with return code "
                f"{completed.returncode}"
            )

        return result

    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")

        if required:
            raise

        return {
            "name": name,
            "script": script,
            "passed": False,
            "return_code": -1,
            "error": str(exc),
        }


# ============================================================
# REPAIR EXTRACTION
# ============================================================

def extract_repairs() -> list[dict[str, Any]]:
    """
    Extract proposed repairs from repair-plan.json.

    Supports several common report layouts so the orchestrator
    does not depend on one exact repair planner implementation.
    """

    report = load_json("repair-plan.json", {})

    if not isinstance(report, dict):
        return []

    possible_lists = [
        report.get("repairs"),
        report.get("problems"),
        report.get("issues"),
        report.get("repair_plan"),
        report.get("plans"),
    ]

    raw_repairs = None

    for candidate in possible_lists:
        if isinstance(candidate, list):
            raw_repairs = candidate
            break

    if raw_repairs is None:
        return []

    repairs: list[dict[str, Any]] = []

    for item in raw_repairs:
        if not isinstance(item, dict):
            continue

        repair = dict(item)

        file_value = (
            repair.get("file")
            or repair.get("path")
            or repair.get("target")
            or repair.get("affected_file")
        )

        if not file_value:
            continue

        normalized = normalize_path(file_value)

        if not is_real_project_file(normalized):
            continue

        repair["file"] = normalized

        repairs.append(repair)

    return repairs


# ============================================================
# DEPENDENCY GRAPH
# ============================================================

def extract_dependency_graph() -> dict[str, set[str]]:
    """
    Build:

        target_file -> files that may depend on target_file

    The dependency analyzer may report generated files,
    backups, and reports. Those are deliberately removed.
    """

    report = load_json("dependencies.json", {})

    graph: dict[str, set[str]] = {}

    def add_edge(target: str, dependent: str) -> None:
        target = normalize_path(target)
        dependent = normalize_path(dependent)

        if not is_real_project_file(target):
            return

        if not is_real_project_file(dependent):
            return

        if target == dependent:
            return

        graph.setdefault(target, set()).add(dependent)

    # --------------------------------------------------------
    # Format A:
    #
    # {
    #   "dependencies": {
    #       "src/a.js": ["src/b.js"]
    #   }
    # }
    # --------------------------------------------------------

    if isinstance(report, dict):

        dependencies = report.get("dependencies")

        if isinstance(dependencies, dict):

            for target, dependents in dependencies.items():

                if isinstance(dependents, list):

                    for dependent in dependents:
                        if isinstance(dependent, str):
                            add_edge(target, dependent)

                elif isinstance(dependents, dict):

                    for dependent in dependents.keys():
                        add_edge(target, dependent)

        # ----------------------------------------------------
        # Format B:
        #
        # {
        #   "files": [
        #       {
        #           "file": "...",
        #           "dependencies": [...]
        #       }
        #   ]
        # }
        # ----------------------------------------------------

        files = report.get("files")

        if isinstance(files, list):

            for entry in files:

                if not isinstance(entry, dict):
                    continue

                target = (
                    entry.get("file")
                    or entry.get("path")
                    or entry.get("target")
                )

                if not target:
                    continue

                dependents = (
                    entry.get("dependents")
                    or entry.get("used_by")
                    or entry.get("references")
                )

                if isinstance(dependents, list):

                    for dependent in dependents:

                        if isinstance(dependent, str):
                            add_edge(target, dependent)

    return graph


# ============================================================
# RECURSIVE DEPENDENT DISCOVERY
# ============================================================

def discover_dependents(
    original_files: list[str],
    graph: dict[str, set[str]],
) -> tuple[list[str], list[dict[str, Any]]]:

    discovered: set[str] = set()
    edges: list[dict[str, Any]] = []

    queue: list[tuple[str, int, str | None]] = []

    for file in original_files:
        normalized = normalize_path(file)

        if is_real_project_file(normalized):
            queue.append((normalized, 0, None))

    while queue:

        current, depth, parent = queue.pop(0)

        if depth >= MAX_DEPENDENT_DEPTH:
            continue

        for dependent in sorted(graph.get(current, set())):

            dependent = normalize_path(dependent)

            if not is_real_project_file(dependent):
                continue

            if dependent in discovered:
                continue

            discovered.add(dependent)

            edge = {
                "source": current,
                "dependent": dependent,
                "depth": depth + 1,
            }

            edges.append(edge)

            queue.append(
                (
                    dependent,
                    depth + 1,
                    current,
                )
            )

    return sorted(discovered), edges


# ============================================================
# COMPLETE FIX SET
# ============================================================

def build_complete_fix_set(
    repairs: list[dict[str, Any]],
    dependent_files: list[str],
) -> list[dict[str, Any]]:

    fix_set: list[dict[str, Any]] = []

    seen: set[str] = set()

    for repair in repairs:

        file = normalize_path(repair["file"])

        if file in seen:
            continue

        seen.add(file)

        item = dict(repair)

        item["fix_role"] = "original"

        fix_set.append(item)

    for file in dependent_files:

        file = normalize_path(file)

        if file in seen:
            continue

        seen.add(file)

        fix_set.append(
            {
                "file": file,
                "fix_role": "dependent",
                "reason": "Affected by an upstream proposed repair",
            }
        )

    return fix_set


# ============================================================
# COMPLETE FIX-SET SIGNATURE
# ============================================================

def fix_set_signature(
    fix_set: list[dict[str, Any]]
) -> list[str]:

    return sorted(
        {
            normalize_path(item["file"])
            for item in fix_set
            if item.get("file")
            and is_real_project_file(item["file"])
        }
    )


# ============================================================
# DEPENDENT IMPACT REPORT
# ============================================================

def save_orchestrator_dependent_report(
    original_repairs: list[dict[str, Any]],
    dependent_files: list[str],
    edges: list[dict[str, Any]],
    fix_set: list[dict[str, Any]],
    iteration: int,
) -> None:

    report = {
        "started": now(),
        "recursive": True,
        "maximum_depth": MAX_DEPENDENT_DEPTH,
        "iteration": iteration,

        "original_repairs": len(original_repairs),

        "original_files": [
            normalize_path(r["file"])
            for r in original_repairs
        ],

        "dependent_files": dependent_files,

        "dependency_edges": edges,

        "complete_fix_set": fix_set_signature(fix_set),

        "complete_fix_set_count": len(fix_set),

        "automatic_modification": AUTOMATIC_MODIFICATION,

        "generated_files_excluded": True,

        "excluded_roots": sorted(IGNORED_ROOTS),

        "completed": now(),
    }

    save_json(
        "orchestrator-dependent-analysis.json",
        report,
    )


# ============================================================
# RE-RUN ANALYSIS
# ============================================================

def rerun_complete_analysis() -> list[dict[str, Any]]:
    """
    Re-run the analysis stages after the repair set changes.

    IMPORTANT:
    We do NOT run repair_engine here.

    This stage only asks the analysis system whether the
    complete proposed repair set is still safe.
    """

    results: list[dict[str, Any]] = []

    analysis_steps = [
        ("Dependency Analyzer", "dependency.py"),
        ("Impact Analyzer", "impact.py"),
        ("Repair Planner", "repair.py"),
        ("Pre-Fix Impact Analyzer", "prefix.py"),
        ("Dependent-Fix Impact Analyzer", "dependent_impact.py"),
    ]

    for name, script in analysis_steps:
        results.append(
            run_step(
                name,
                script,
                required=True,
            )
        )

    return results


# ============================================================
# COMPLETE FIX-SET SAFETY EVALUATION
# ============================================================

def evaluate_complete_fix_set(
    fix_set: list[dict[str, Any]],
) -> tuple[bool, list[str]]:

    reasons: list[str] = []

    if not fix_set:
        reasons.append(
            "The current repair plan contains no repairs."
        )

        return False, reasons

    # --------------------------------------------------------
    # Check every target
    # --------------------------------------------------------

    for item in fix_set:

        file = normalize_path(item.get("file", ""))

        if not file:
            reasons.append(
                "A proposed repair has no target file."
            )
            continue

        if not is_real_project_file(file):
            reasons.append(
                f"Proposed repair target does not exist: {file}"
            )

    # --------------------------------------------------------
    # Safety reports
    # --------------------------------------------------------

    safety = load_json("safety.json", {})

    if isinstance(safety, dict):

        if safety.get("passed") is False:
            reasons.append(
                "Safety report did not approve the proposed repair set."
            )

        decision = str(
            safety.get("final_decision", "")
        ).upper()

        if decision in {
            "BLOCKED",
            "NO REPAIR NEEDED",
            "DENIED",
        }:
            reasons.append(
                f"Safety gate decision: {decision}"
            )

    # --------------------------------------------------------
    # Pre-fix analysis
    # --------------------------------------------------------

    prefix = load_json("prefix.json", {})

    if isinstance(prefix, dict):

        if prefix.get("passed") is False:
            reasons.append(
                "Pre-fix impact analysis did not pass."
            )

        decision = str(
            prefix.get("final_decision", "")
        ).upper()

        if decision in {
            "BLOCKED",
            "DENIED",
        }:
            reasons.append(
                f"Pre-fix analysis decision: {decision}"
            )

    # --------------------------------------------------------
    # Dependent impact
    # --------------------------------------------------------

    dependent = load_json(
        "dependent-impact.json",
        {},
    )

    if isinstance(dependent, dict):

        if dependent.get("passed") is False:
            reasons.append(
                "Dependent-fix impact analysis did not pass."
            )

        decision = str(
            dependent.get("final_decision", "")
        ).upper()

        if decision in {
            "BLOCKED",
            "DENIED",
        }:
            reasons.append(
                f"Dependent impact decision: {decision}"
            )

    # --------------------------------------------------------
    # Automatic modification remains disabled.
    # --------------------------------------------------------

    if not AUTOMATIC_MODIFICATION:
        reasons.append(
            "Automatic modification is disabled."
        )

    return len(reasons) == 0, reasons


# ============================================================
# DEPENDENT REPAIR PIPELINE
# ============================================================

def analyze_dependent_repairs() -> dict[str, Any]:

    print()
    print("=" * 58)
    print(" EAST SMP DEPENDENT REPAIR ANALYSIS")
    print("=" * 58)

    repairs = extract_repairs()

    original_files = [
        normalize_path(repair["file"])
        for repair in repairs
    ]

    print()
    print(f"[REPAIRS] Original repairs: {len(repairs)}")

    if not repairs:
        print("[REPAIRS] No repairs currently proposed.")

        return {
            "original_repairs": [],
            "dependent_files": [],
            "complete_fix_set": [],
            "edges": [],
            "iterations": 0,
            "stable": True,
        }

    graph = extract_dependency_graph()

    previous_signature: list[str] = []

    all_edges: list[dict[str, Any]] = []

    complete_fix_set: list[dict[str, Any]] = []

    for iteration in range(1, MAX_DEPENDENT_DEPTH + 1):

        print()
        print(
            f"[DEPENDENCY ANALYSIS] "
            f"Iteration {iteration}/{MAX_DEPENDENT_DEPTH}"
        )

        dependent_files, edges = discover_dependents(
            original_files,
            graph,
        )

        all_edges = edges

        complete_fix_set = build_complete_fix_set(
            repairs,
            dependent_files,
        )

        current_signature = fix_set_signature(
            complete_fix_set
        )

        save_orchestrator_dependent_report(
            repairs,
            dependent_files,
            edges,
            complete_fix_set,
            iteration,
        )

        print(
            f"[DEPENDENTS] "
            f"{len(dependent_files)} discovered"
        )

        print(
            f"[COMPLETE FIX SET] "
            f"{len(complete_fix_set)} files"
        )

        # ----------------------------------------------------
        # Stable?
        # ----------------------------------------------------

        if current_signature == previous_signature:

            print(
                "[DEPENDENCY ANALYSIS] "
                "Complete fix set is stable."
            )

            return {
                "original_repairs": repairs,
                "dependent_files": dependent_files,
                "complete_fix_set": complete_fix_set,
                "edges": all_edges,
                "iterations": iteration,
                "stable": True,
            }

        previous_signature = current_signature

        # ----------------------------------------------------
        # Re-run all analysis after each expansion.
        # ----------------------------------------------------

        if iteration < MAX_DEPENDENT_DEPTH:

            print(
                "[REANALYSIS] "
                "Re-analyzing complete proposed change..."
            )

            rerun_complete_analysis()

            # Reload repairs because the repair planner may
            # discover additional problems caused by the
            # expanded repair set.
            new_repairs = extract_repairs()

            if new_repairs:
                repairs = new_repairs

                original_files = [
                    normalize_path(r["file"])
                    for r in repairs
                ]

                graph = extract_dependency_graph()

    print(
        "[BLOCKED] "
        "Maximum dependent-analysis depth reached."
    )

    return {
        "original_repairs": repairs,
        "dependent_files": [
            item["file"]
            for item in complete_fix_set
            if item.get("fix_role") == "dependent"
        ],
        "complete_fix_set": complete_fix_set,
        "edges": all_edges,
        "iterations": MAX_DEPENDENT_DEPTH,
        "stable": False,
    }


# ============================================================
# VERIFIED BACKUP REQUIREMENT
# ============================================================

def backup_is_verified() -> bool:

    backup = load_json("backup.json", {})

    if not isinstance(backup, dict):
        return False

    if backup.get("verified") is True:
        return True

    if str(
        backup.get("status", "")
    ).upper() == "VERIFIED":
        return True

    return False


# ============================================================
# POST-CHANGE VERIFICATION
# ============================================================

def verification_passed() -> bool:

    report = load_json("verification.json", {})

    if not isinstance(report, dict):
        return False

    if report.get("passed") is False:
        return False

    # Scanner failures
    failed_tests = report.get("failed_tests")

    if isinstance(failed_tests, int) and failed_tests > 0:
        return False

    scanner_failed = report.get("scanner_failed")

    if scanner_failed is True:
        return False

    # Build failure
    build_passed = report.get("build_passed")

    if build_passed is False:
        return False

    return True


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def main() -> int:

    started = now()

    print()
    print("=" * 60)
    print(" EAST SMP AI ORCHESTRATOR")
    print(" DEPENDENT REPAIR SAFETY PIPELINE")
    print("=" * 60)

    steps: list[dict[str, Any]] = []

    # ========================================================
    # INITIAL ANALYSIS
    # ========================================================

    pipeline = [
        ("Scanner", "scanner.py"),
        ("Dependency Analyzer", "dependency.py"),
        ("Impact Analyzer", "impact.py"),
        ("Repair Planner", "repair.py"),
        ("Pre-Fix Impact Analyzer", "prefix.py"),
        ("Dependent-Fix Impact Analyzer", "dependent_impact.py"),
    ]

    try:

        for name, script in pipeline:

            result = run_step(
                name,
                script,
                required=True,
            )

            steps.append(result)

    except Exception as exc:

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",
                "pipeline_passed": False,
                "automatic_modification": AUTOMATIC_MODIFICATION,
                "error": str(exc),
                "steps": steps,
                "final_decision": "BLOCKED",
            },
        )

        return 1

    # ========================================================
    # DEPENDENT ANALYSIS
    # ========================================================

    dependent_result = analyze_dependent_repairs()

    original_repairs = dependent_result[
        "original_repairs"
    ]

    dependent_files = dependent_result[
        "dependent_files"
    ]

    complete_fix_set = dependent_result[
        "complete_fix_set"
    ]

    stable = dependent_result["stable"]

    print()
    print("=" * 58)
    print(" COMPLETE PROPOSED FIX SET")
    print("=" * 58)

    print(
        f"[REPAIRS] Original: {len(original_repairs)}"
    )

    print(
        f"[FILES] Dependent: {len(dependent_files)}"
    )

    print(
        f"[FILES] Complete set: {len(complete_fix_set)}"
    )

    if not stable:

        print(
            "[SAFETY] "
            "Dependent repair analysis did not stabilize."
        )

        final_decision = "BLOCKED"

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",
                "pipeline_passed": True,
                "automatic_modification": AUTOMATIC_MODIFICATION,

                "repairs": {
                    "original_count": len(original_repairs),
                    "original_files": [
                        r["file"]
                        for r in original_repairs
                    ],
                    "dependent_files": dependent_files,
                    "complete_fix_set": fix_set_signature(
                        complete_fix_set
                    ),
                },

                "dependent_analysis": {
                    "recursive": True,
                    "maximum_depth": MAX_DEPENDENT_DEPTH,
                    "iterations": dependent_result[
                        "iterations"
                    ],
                    "completed": False,
                },

                "repair_permission": {
                    "allowed": False,
                    "reason": "DEPENDENT_ANALYSIS_UNSTABLE",
                },

                "steps": steps,

                "files_modified": 0,

                "final_decision": final_decision,
            },
        )

        return 0

    # ========================================================
    # COMPLETE FIX SET MUST BE RE-ANALYZED
    # ========================================================

    print()
    print(
        "[SAFETY] Evaluating complete proposed fix set..."
    )

    # Re-run the safety-related analyzers one final time.
    try:

        final_analysis_steps = [
            ("Dependency Analyzer", "dependency.py"),
            ("Impact Analyzer", "impact.py"),
            ("Repair Planner", "repair.py"),
            ("Pre-Fix Impact Analyzer", "prefix.py"),
            ("Dependent-Fix Impact Analyzer", "dependent_impact.py"),
            ("Safety Gate", "safety.py"),
        ]

        for name, script in final_analysis_steps:

            result = run_step(
                name,
                script,
                required=True,
            )

            steps.append(result)

    except Exception as exc:

        print(
            f"[FINAL SAFETY] Analysis failed: {exc}"
        )

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",
                "pipeline_passed": False,
                "automatic_modification": AUTOMATIC_MODIFICATION,
                "error": str(exc),
                "final_decision": "BLOCKED",
            },
        )

        return 0

    # Reload the final repair plan because the final analysis
    # may have changed it.
    final_repairs = extract_repairs()

    final_graph = extract_dependency_graph()

    final_original_files = [
        normalize_path(r["file"])
        for r in final_repairs
    ]

    final_dependents, final_edges = discover_dependents(
        final_original_files,
        final_graph,
    )

    final_fix_set = build_complete_fix_set(
        final_repairs,
        final_dependents,
    )

    # If the repair set changed after final analysis,
    # BLOCK instead of silently approving a different set.
    previous_set = set(
        fix_set_signature(complete_fix_set)
    )

    final_set = set(
        fix_set_signature(final_fix_set)
    )

    if previous_set != final_set:

        print()
        print(
            "[SAFETY] Complete fix set changed during "
            "final analysis."
        )

        print(
            "[SAFETY] Another complete dependent analysis "
            "is required."
        )

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",

                "pipeline_passed": True,

                "automatic_modification":
                    AUTOMATIC_MODIFICATION,

                "repairs": {
                    "original_count":
                        len(final_repairs),

                    "original_files":
                        final_original_files,

                    "dependent_files":
                        final_dependents,

                    "complete_fix_set":
                        sorted(final_set),
                },

                "dependent_analysis": {
                    "recursive": True,
                    "maximum_depth":
                        MAX_DEPENDENT_DEPTH,

                    "completed": False,

                    "reason":
                        "FINAL_FIX_SET_CHANGED",
                },

                "repair_permission": {
                    "allowed": False,
                    "reason":
                        "COMPLETE_FIX_SET_CHANGED",
                },

                "files_modified": 0,

                "final_decision": "BLOCKED",
            },
        )

        return 0

    # ========================================================
    # SAFETY EVALUATION
    # ========================================================

    approved, reasons = evaluate_complete_fix_set(
        final_fix_set
    )

    print()
    print("=" * 58)
    print("[FINAL REPAIR DECISION]")
    print("=" * 58)

    if not approved:

        print("[FINAL REPAIR DECISION] BLOCKED")

        for reason in reasons:
            print(f"- {reason}")

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",

                "pipeline_passed": True,

                "automatic_modification":
                    AUTOMATIC_MODIFICATION,

                "repairs": {
                    "original_count":
                        len(final_repairs),

                    "original_files":
                        final_original_files,

                    "dependent_files":
                        final_dependents,

                    "complete_fix_set":
                        sorted(final_set),
                },

                "dependent_analysis": {
                    "recursive": True,
                    "maximum_depth":
                        MAX_DEPENDENT_DEPTH,

                    "completed": True,

                    "edges": final_edges,
                },

                "repair_permission": {
                    "allowed": False,
                    "reason":
                        "SAFETY_ANALYSIS_BLOCKED",

                    "reasons": reasons,
                },

                "files_modified": 0,

                "final_decision": "BLOCKED",
            },
        )

        return 0

    # ========================================================
    # VERIFIED BACKUP
    # ========================================================

    print()
    print(
        "[SAFETY] Complete fix set passed analysis."
    )

    print(
        "[SAFETY] A VERIFIED BACKUP is required "
        "before any modification."
    )

    # The orchestrator itself does not create the backup.
    # It invokes the existing backup system.
    backup_result = run_step(
        "Backup System",
        "backup.py",
        required=True,
    )

    steps.append(backup_result)

    if not backup_is_verified():

        print(
            "[FINAL SAFETY DECISION] BLOCKED"
        )

        print(
            "[SAFETY] Backup was not verified."
        )

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",

                "pipeline_passed": True,

                "automatic_modification":
                    AUTOMATIC_MODIFICATION,

                "repair_permission": {
                    "allowed": False,
                    "reason":
                        "BACKUP_NOT_VERIFIED",
                },

                "files_modified": 0,

                "final_decision": "BLOCKED",
            },
        )

        return 0

    print(
        "[SAFETY] Verified backup exists."
    )

    # ========================================================
    # AUTOMATIC MODIFICATION IS STILL DISABLED
    # ========================================================

    if not AUTOMATIC_MODIFICATION:

        print()
        print(
            "[FINAL SAFETY DECISION] "
            "ANALYSIS PASSED / EXECUTION BLOCKED"
        )

        print(
            "[SAFETY] The complete dependent fix set "
            "passed analysis."
        )

        print(
            "[SAFETY] A verified backup exists."
        )

        print(
            "[SAFETY] Automatic modification remains disabled."
        )

        print(
            "[SAFETY] No project files will be modified."
        )

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",

                "pipeline_passed": True,

                "automatic_modification":
                    AUTOMATIC_MODIFICATION,

                "repairs": {
                    "original_count":
                        len(final_repairs),

                    "original_files":
                        final_original_files,

                    "dependent_files":
                        final_dependents,

                    "complete_fix_set":
                        sorted(final_set),
                },

                "dependent_analysis": {
                    "recursive": True,
                    "maximum_depth":
                        MAX_DEPENDENT_DEPTH,

                    "completed": True,

                    "edges": final_edges,
                },

                "repair_permission": {
                    "allowed": False,

                    "reason":
                        "AUTOMATIC_MODIFICATION_DISABLED",

                    "reasons": [
                        "Complete fix set passed analysis.",
                        "Verified backup exists.",
                        "Automatic modification is disabled.",
                    ],
                },

                "files_modified": 0,

                "final_decision":
                    "ANALYSIS_PASSED_EXECUTION_BLOCKED",

                "steps": steps,
            },
        )

        return 0

    # ========================================================
    # REPAIR ENGINE
    # ========================================================

    repair_result = run_step(
        "Repair Engine",
        "repair_engine.py",
        required=True,
    )

    steps.append(repair_result)

    # ========================================================
    # POST-CHANGE VERIFICATION
    # ========================================================

    verify_result = run_step(
        "Verification",
        "verify.py",
        required=False,
    )

    steps.append(verify_result)

    if not verification_passed():

        print()
        print(
            "[SAFETY] Post-change verification FAILED."
        )

        print(
            "[ROLLBACK] Rollback is required."
        )

        # IMPORTANT:
        # Rollback happens before the operation can be
        # considered successful.
        rollback_result = run_step(
            "Rollback",
            "rollback.py",
            required=False,
        )

        steps.append(rollback_result)

        save_json(
            "orchestrator.json",
            {
                "started": started,
                "completed": now(),
                "project": "East SMP",

                "pipeline_passed": False,

                "automatic_modification":
                    AUTOMATIC_MODIFICATION,

                "repairs": {
                    "original_count":
                        len(final_repairs),

                    "original_files":
                        final_original_files,

                    "dependent_files":
                        final_dependents,

                    "complete_fix_set":
                        sorted(final_set),
                },

                "files_modified":
                    "ROLLED_BACK",

                "rollback": {
                    "required": True,
                    "attempted": True,
                    "verification_passed": False,
                },

                "steps": steps,

                "final_decision":
                    "ROLLBACK_REQUIRED",
            },
        )

        return 1

    # ========================================================
    # SUCCESS
    # ========================================================

    print()
    print(
        "[FINAL SAFETY DECISION] "
        "REPAIR + VERIFICATION PASSED"
    )

    save_json(
        "orchestrator.json",
        {
            "started": started,
            "completed": now(),
            "project": "East SMP",

            "pipeline_passed": True,

            "automatic_modification":
                AUTOMATIC_MODIFICATION,

            "repairs": {
                "original_count":
                    len(final_repairs),

                "original_files":
                    final_original_files,

                "dependent_files":
                    final_dependents,

                "complete_fix_set":
                    sorted(final_set),
            },

            "dependent_analysis": {
                "recursive": True,
                "maximum_depth":
                    MAX_DEPENDENT_DEPTH,

                "completed": True,

                "edges": final_edges,
            },

            "files_modified":
                len(final_set),

            "verification": {
                "passed": True,
            },

            "steps": steps,

            "final_decision":
                "REPAIR_VERIFIED",
        },
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("[STOPPED] Orchestrator interrupted.")
        sys.exit(130)
    except Exception as exc:
        print()
        print("=" * 58)
        print("[FATAL] ORCHESTRATOR ERROR")
        print("=" * 58)
        print(exc)

        save_json(
            "orchestrator.json",
            {
                "started": now(),
                "completed": now(),
                "project": "East SMP",
                "pipeline_passed": False,
                "automatic_modification":
                    AUTOMATIC_MODIFICATION,
                "error": str(exc),
                "final_decision": "BLOCKED",
            },
        )

        sys.exit(1)
