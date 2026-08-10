from pathlib import Path
import json


# ==========================================
# EAST SMP AI IMPACT ANALYZER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "scanner.json"


def load_report():
    if not REPORT_FILE.exists():
        print("[ERROR] scanner.json was not found.")
        return None

    try:
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print(f"[ERROR] Could not read scanner.json: {error}")
        return None


def analyze_impact(issue):
    """
    Predict what parts of the project could be affected
    if this issue is eventually repaired.
    """

    name = issue.get("name", "Unknown")
    details = issue.get("details", "")

    affected = []
    risks = []

    # ------------------------------------------
    # CONSOLE / 404
    # ------------------------------------------

    if name == "Console Error Detector":

        affected = [
            "src/pages",
            "src/layouts",
            "src/components",
            "src/scripts",
            "public",
            "astro.config.mjs"
        ]

        risks = [
            "Fixing the wrong route could break navigation.",
            "Changing Astro routing could affect multiple pages.",
            "Changing layout links could create additional broken links.",
            "Removing a resource without checking dependencies could break another page."
        ]

    # ------------------------------------------
    # SPEED
    # ------------------------------------------

    elif name == "Load Speed Rating":

        affected = [
            "src/pages",
            "src/components",
            "src/scripts",
            "src/styles",
            "public"
        ]

        risks = [
            "Removing assets could change page appearance.",
            "Changing scripts could break interactive features.",
            "Changing CSS could affect mobile compatibility.",
            "Optimizing the wrong resource may provide no performance improvement."
        ]

    # ------------------------------------------
    # UNKNOWN
    # ------------------------------------------

    else:

        affected = [
            "Unknown project files"
        ]

        risks = [
            "The cause has not been identified yet.",
            "Automatic modification would be unsafe."
        ]

    return {
        "issue": name,
        "details": details,
        "affected_areas": affected,
        "risks": risks
    }


def main():

    report = load_report()

    if report is None:
        return

    failures = [
        result
        for result in report
        if not result.get("passed", False)
    ]

    print()
    print("==========================================")
    print(" EAST SMP AI IMPACT ANALYZER")
    print("==========================================")

    if not failures:

        print()
        print("[AI] No failed tests.")
        print("[AI] No impact analysis required.")
        return

    all_analysis = []

    for issue in failures:

        analysis = analyze_impact(issue)

        all_analysis.append(analysis)

        print()
        print("------------------------------------------")
        print(f"ISSUE: {analysis['issue']}")
        print("------------------------------------------")

        print()
        print("AFFECTED AREAS:")

        for area in analysis["affected_areas"]:
            print(f"  - {area}")

        print()
        print("POTENTIAL RISKS:")

        for risk in analysis["risks"]:
            print(f"  - {risk}")

    # ------------------------------------------
    # SAVE IMPACT REPORT
    # ------------------------------------------

    output_dir = PROJECT_ROOT / "reports"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "impact.json"

    with output_file.open("w", encoding="utf-8") as file:

        json.dump(
            all_analysis,
            file,
            indent=2
        )

    print()
    print("==========================================")
    print(" IMPACT ANALYSIS COMPLETE")
    print("==========================================")
    print()
    print(f"Report saved: {output_file}")


if __name__ == "__main__":
    main()