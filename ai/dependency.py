from pathlib import Path
import json
import re

# ==========================================
# EAST SMP AI DEPENDENCY ANALYZER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMPACT_FILE = PROJECT_ROOT / "reports" / "impact.json"
DEPENDENCY_FILE = PROJECT_ROOT / "reports" / "dependencies.json"


# ==========================================
# DIRECTORIES THAT MUST NEVER BE ANALYZED
# ==========================================

EXCLUDED_DIRECTORIES = {
    "node_modules",
    ".git",
    ".astro",
    "dist",
    "__pycache__",
    ".pytest_cache",
    "backups",
    "reports",
}


# ==========================================
# LOAD IMPACT REPORT
# ==========================================

def load_impact():

    if not IMPACT_FILE.exists():

        print("[ERROR] impact.json was not found.")
        print(f"Expected: {IMPACT_FILE}")

        return None

    try:

        with IMPACT_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError as error:

        print("[ERROR] impact.json contains invalid JSON.")
        print(error)

        return None


# ==========================================
# CHECK WHETHER A PATH IS EXCLUDED
# ==========================================

def is_excluded(path):

    return any(
        part in EXCLUDED_DIRECTORIES
        for part in path.parts
    )


# ==========================================
# SCAN PROJECT FILES
# ==========================================

def get_project_files():

    extensions = {
        ".astro",
        ".js",
        ".ts",
        ".css",
        ".json",
        ".html",
        ".py"
    }

    files = []

    # Use os.walk-style pruning through Path.rglob filtering.
    # Any file inside an excluded directory is ignored.

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if is_excluded(path):
            continue

        if path.suffix.lower() not in extensions:
            continue

        files.append(path)

    return files


# ==========================================
# READ FILE
# ==========================================

def read_file(path):

    try:

        return path.read_text(
            encoding="utf-8"
        )

    except (
        OSError,
        UnicodeDecodeError
    ):

        return ""


# ==========================================
# FIND REFERENCES
# ==========================================

def find_references(files):

    references = {}

    for path in files:

        content = read_file(path)

        if not content:
            continue

        relative = path.relative_to(
            PROJECT_ROOT
        ).as_posix()

        found = []

        # --------------------------------------
        # ES MODULE IMPORTS
        # --------------------------------------

        import_matches = re.findall(
            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
            content
        )

        # --------------------------------------
        # SIDE-EFFECT IMPORTS
        # --------------------------------------

        side_effect_imports = re.findall(
            r'import\s+[\'"](.+?)[\'"]',
            content
        )

        # --------------------------------------
        # CSS IMPORTS
        # --------------------------------------

        css_matches = re.findall(
            r'@import\s+[\'"](.+?)[\'"]',
            content
        )

        # --------------------------------------
        # COMMONJS REQUIRE
        # --------------------------------------

        require_matches = re.findall(
            r'require\s*\(\s*[\'"](.+?)[\'"]\s*\)',
            content
        )

        found.extend(import_matches)
        found.extend(side_effect_imports)
        found.extend(css_matches)
        found.extend(require_matches)

        references[relative] = list(
            dict.fromkeys(found)
        )

    return references


# ==========================================
# FIND FILES THAT REFERENCE ANOTHER FILE
# ==========================================

def find_dependents(files):

    dependents = {}

    # Cache file contents so the same files are
    # not repeatedly read from disk.

    contents = {}

    for path in files:

        contents[path] = read_file(path)

    for target in files:

        target_relative = target.relative_to(
            PROJECT_ROOT
        ).as_posix()

        target_name = target.name

        dependents[target_relative] = []

        for source in files:

            if source == target:
                continue

            content = contents.get(
                source,
                ""
            )

            if not content:
                continue

            source_relative = source.relative_to(
                PROJECT_ROOT
            ).as_posix()

            # ----------------------------------
            # Ignore self-generated report paths
            # ----------------------------------

            if is_excluded(source):
                continue

            # ----------------------------------
            # Detect filename references
            # ----------------------------------

            if target_name in content:

                dependents[target_relative].append(
                    source_relative
                )

        # Remove duplicates while preserving order

        dependents[target_relative] = list(
            dict.fromkeys(
                dependents[target_relative]
            )
        )

    return dependents


# ==========================================
# ANALYZE RISK
# ==========================================

def analyze_risk(dependent_files):

    count = len(dependent_files)

    if count == 0:

        return {
            "level": "LOW",
            "reason":
                "No direct file references detected."
        }

    if count <= 3:

        return {
            "level": "MEDIUM",
            "reason":
                f"{count} dependent file(s) detected."
        }

    return {
        "level": "HIGH",
        "reason":
            f"{count} dependent files detected."
    }


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI DEPENDENCY ANALYZER")
    print("==========================================")
    print()

    print(
        "[INFO] Excluded directories:"
    )

    for directory in sorted(
        EXCLUDED_DIRECTORIES
    ):

        print(
            f"  - {directory}/"
        )

    print()

    # ======================================
    # LOAD IMPACT REPORT
    # ======================================

    impact = load_impact()

    if impact is None:
        return

    # ======================================
    # SCAN FILES
    # ======================================

    files = get_project_files()

    print(
        f"Project files scanned: {len(files)}"
    )

    print()

    # ======================================
    # FIND REFERENCES
    # ======================================

    references = find_references(
        files
    )

    # ======================================
    # FIND DEPENDENTS
    # ======================================

    dependents = find_dependents(
        files
    )

    # ======================================
    # BUILD REPORT
    # ======================================

    report = {
        "project_files_scanned": len(files),

        "excluded_directories": sorted(
            EXCLUDED_DIRECTORIES
        ),

        "references": references,

        "dependents": {},

        "risks": {}
    }

    # ======================================
    # ANALYZE EACH FILE
    # ======================================

    for target, dependency_list in dependents.items():

        report["dependents"][target] = (
            dependency_list
        )

        report["risks"][target] = (
            analyze_risk(
                dependency_list
            )
        )

    # ======================================
    # PRINT IMPORTANT DEPENDENCIES
    # ======================================

    print(
        "DEPENDENCY RESULTS"
    )

    print()

    dependency_count = 0

    for target, dependency_list in dependents.items():

        if not dependency_list:
            continue

        dependency_count += 1

        print(
            f"[DEPENDENCY] {target}"
        )

        for dependent in dependency_list:

            print(
                f"  <- {dependent}"
            )

        risk = report["risks"][target]

        print(
            f"  Risk: {risk['level']}"
        )

        print()

    # ======================================
    # SUMMARY
    # ======================================

    print(
        "DEPENDENCY SUMMARY"
    )

    print(
        f"Files scanned: {len(files)}"
    )

    print(
        f"Files with dependents: {dependency_count}"
    )

    print()

    # ======================================
    # SAVE REPORT
    # ======================================

    DEPENDENCY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with DEPENDENCY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    print(
        f"Dependency report saved: "
        f"{DEPENDENCY_FILE}"
    )

    print()

    print(
        "[PASS] Dependency Analyzer completed."
    )

    print()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

