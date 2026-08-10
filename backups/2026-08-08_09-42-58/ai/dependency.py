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

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        # Ignore generated / dependency folders
        if any(
            part in {
                "node_modules",
                ".git",
                ".astro",
                "dist",
                "__pycache__"
            }
            for part in path.parts
        ):
            continue

        if path.suffix.lower() in extensions:

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

    except (OSError, UnicodeDecodeError):

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

        # Astro imports
        import_matches = re.findall(
            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
            content
        )

        # CSS imports
        css_matches = re.findall(
            r'@import\s+[\'"](.+?)[\'"]',
            content
        )

        # JavaScript imports
        require_matches = re.findall(
            r'require\s*\(\s*[\'"](.+?)[\'"]\s*\)',
            content
        )

        found.extend(import_matches)
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

    for target in files:

        target_relative = target.relative_to(
            PROJECT_ROOT
        ).as_posix()

        target_name = target.name

        dependents[target_relative] = []

        for source in files:

            if source == target:
                continue

            content = read_file(source)

            if not content:
                continue

            source_relative = source.relative_to(
                PROJECT_ROOT
            ).as_posix()

            if target_name in content:

                dependents[target_relative].append(
                    source_relative
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
            "reason": "No direct file references detected."
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

    impact = load_impact()

    if impact is None:
        return

    files = get_project_files()

    print(
        f"Project files scanned: {len(files)}"
    )

    print()

    references = find_references(
        files
    )

    dependents = find_dependents(
        files
    )

    report = {
        "project_files_scanned": len(files),
        "references": references,
        "dependents": {},
        "risks": {}
    }

    for target, dependency_list in dependents.items():

        report["dependents"][target] = dependency_list

        report["risks"][target] = analyze_risk(
            dependency_list
        )

    # ======================================
    # PRINT IMPORTANT DEPENDENCIES
    # ======================================

    print("DEPENDENCY RESULTS")
    print()

    for target, dependency_list in dependents.items():

        if not dependency_list:
            continue

        print(f"[DEPENDENCY] {target}")

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
        f"Dependency report saved: {DEPENDENCY_FILE}"
    )


if __name__ == "__main__":
    main()
