from pathlib import Path
import json
from datetime import datetime

# ==========================================
# EAST SMP AI HISTORY LOGGER
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = PROJECT_ROOT / "reports"

HISTORY_FILE = REPORTS_DIR / "ai-history.json"

SCANNER_FILE = REPORTS_DIR / "scanner.json"
SAFETY_FILE = REPORTS_DIR / "safety.json"
BACKUP_FILE = REPORTS_DIR / "backup.json"
REPAIR_FILE = REPORTS_DIR / "repair-engine.json"
VERIFICATION_FILE = REPORTS_DIR / "verification.json"


# ==========================================
# LOAD JSON
# ==========================================

def load_json(path):

    if not path.exists():
        return None

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return None


# ==========================================
# LOAD EXISTING HISTORY
# ==========================================

def load_history():

    if not HISTORY_FILE.exists():
        return []

    try:

        with HISTORY_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ==========================================
# GET SCANNER STATUS
# ==========================================

def scanner_summary(data):

    if not data:
        return {
            "available": False
        }

    passed = sum(
        1
        for item in data
        if item.get("passed") is True
    )

    failed = sum(
        1
        for item in data
        if item.get("passed") is False
    )

    total = passed + failed

    if total > 0:
        score = round(
            (passed / total) * 100
        )
    else:
        score = 0

    return {
        "available": True,
        "passed": passed,
        "failed": failed,
        "total": total,
        "health_score": score
    }


# ==========================================
# CREATE HISTORY ENTRY
# ==========================================

def create_history_entry():

    scanner = load_json(
        SCANNER_FILE
    )

    safety = load_json(
        SAFETY_FILE
    )

    backup = load_json(
        BACKUP_FILE
    )

    repair = load_json(
        REPAIR_FILE
    )

    verification = load_json(
        VERIFICATION_FILE
    )

    scanner_info = scanner_summary(
        scanner
    )

    entry = {

        "timestamp":
            datetime.now().isoformat(),

        "project":
            "East SMP",

        "scanner":
            scanner_info,

        "safety": {

            "available":
                safety is not None,

            "automatic_modification_allowed":
                (
                    safety.get(
                        "automatic_modification_allowed",
                        False
                    )
                    if safety
                    else False
                ),

            "final_decision":
                (
                    safety.get(
                        "final_safety_decision",
                        safety.get(
                            "status",
                            "UNKNOWN"
                        )
                    )
                    if safety
                    else "UNKNOWN"
                )
        },

        "backup": {

            "available":
                backup is not None,

            "verified":
                (
                    backup.get(
                        "verified",
                        False
                    )
                    if backup
                    else False
                )
        },

        "repair_engine": {

            "available":
                repair is not None,

            "mode":
                (
                    repair.get(
                        "mode",
                        "UNKNOWN"
                    )
                    if repair
                    else "UNKNOWN"
                ),

            "proposals":
                (
                    repair.get(
                        "repair_proposals",
                        0
                    )
                    if repair
                    else 0
                ),

            "files_modified":
                (
                    repair.get(
                        "files_modified",
                        []
                    )
                    if repair
                    else []
                ),

            "automatic_execution":
                (
                    repair.get(
                        "automatic_execution",
                        False
                    )
                    if repair
                    else False
                )
        },

        "verification": {

            "available":
                verification is not None,

            "status":
                (
                    verification.get(
                        "status",
                        verification.get(
                            "final_verification",
                            "UNKNOWN"
                        )
                    )
                    if verification
                    else "UNKNOWN"
                )
        }

    }

    return entry


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI HISTORY LOGGER")
    print("==========================================")
    print()

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    history = load_history()

    entry = create_history_entry()

    history.append(
        entry
    )

    with HISTORY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=2
        )

    print(
        "[HISTORY] New AI operation recorded."
    )

    print(
        f"[HISTORY] Total recorded operations: "
        f"{len(history)}"
    )

    print()

    print(
        "[PROJECT] East SMP"
    )

    print(
        f"[HEALTH] "
        f"{entry['scanner'].get('health_score', 0)}%"
    )

    print(
        f"[REPAIRS] "
        f"{entry['repair_engine']['proposals']}"
    )

    print(
        f"[FILES MODIFIED] "
        f"{len(entry['repair_engine']['files_modified'])}"
    )

    print(
        "[AUTOMATIC MODIFICATION] DISABLED"
    )

    print()

    print(
        f"History saved: {HISTORY_FILE}"
    )

    print()

    print(
        "[FINAL SAFETY STATUS] LOGGING ONLY"
    )

    print(
        "[SAFETY] This script does not modify project files."
    )

    print()


if __name__ == "__main__":
    main()

