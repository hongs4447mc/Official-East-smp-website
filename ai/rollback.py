from pathlib import Path
import json

# ==========================================
# EAST SMP AI ROLLBACK SYSTEM
# ==========================================
#
# SAFETY RULE:
# This version ONLY verifies backups and
# prepares a rollback plan.
#
# It DOES NOT:
# - restore files
# - delete files
# - overwrite project files
# - modify the website
#
# Current mode: ROLLBACK PREVIEW
# ==========================================


PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKUPS_DIR = PROJECT_ROOT / "backups"
REPORTS_DIR = PROJECT_ROOT / "reports"

BACKUP_REPORT = REPORTS_DIR / "backup.json"
VERIFICATION_REPORT = REPORTS_DIR / "verification.json"

ROLLBACK_REPORT = REPORTS_DIR / "rollback.json"


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

        print(
            f"[ERROR] {name} contains invalid JSON."
        )

        print(error)

        return None

    except OSError as error:

        print(
            f"[ERROR] Could not read {name}."
        )

        print(error)

        return None


# ==========================================
# FIND BACKUPS
# ==========================================

def find_backups():

    if not BACKUPS_DIR.exists():
        return []

    backups = []

    for item in BACKUPS_DIR.iterdir():

        if item.is_dir():

            backups.append(item)

    return sorted(
        backups,
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )


# ==========================================
# VERIFY BACKUP DIRECTORY
# ==========================================

def verify_backup_directory(backup):

    if not backup.exists():
        return False

    if not backup.is_dir():
        return False

    try:

        files = list(
            backup.rglob("*")
        )

        # A valid backup should contain
        # at least one file.

        return any(
            item.is_file()
            for item in files
        )

    except OSError:

        return False


# ==========================================
# VERIFY BACKUP REPORT
# ==========================================

def verify_backup_report():

    data = load_json(
        BACKUP_REPORT,
        "backup.json"
    )

    if data is None:
        return False

    verified = data.get(
        "verified",
        False
    )

    return verified is True


# ==========================================
# CHECK PROJECT VERIFICATION
# ==========================================

def verification_status():

    data = load_json(
        VERIFICATION_REPORT,
        "verification.json"
    )

    if data is None:
        return "UNKNOWN"

    # Support several possible report formats.

    if data.get("passed") is True:
        return "PASSED"

    if data.get("verification_passed") is True:
        return "PASSED"

    status = str(
        data.get(
            "status",
            ""
        )
    ).upper()

    if status == "PASSED":
        return "PASSED"

    final_status = str(
        data.get(
            "final_verification",
            ""
        )
    ).upper()

    if final_status == "PASSED":
        return "PASSED"

    return "UNKNOWN"


# ==========================================
# CREATE ROLLBACK PLAN
# ==========================================

def create_rollback_plan():

    backups = find_backups()

    latest_backup = None

    if backups:

        for backup in backups:

            if verify_backup_directory(
                backup
            ):

                latest_backup = backup

                break

    backup_report_verified = (
        verify_backup_report()
    )

    verification = verification_status()

    rollback_required = (
        verification == "FAILED"
    )

    return {

        "mode":
            "ROLLBACK_PREVIEW",

        "automatic_rollback":
            False,

        "rollback_required":
            rollback_required,

        "verification_status":
            verification,

        "backup_report_verified":
            backup_report_verified,

        "available_backups":
            len(backups),

        "latest_verified_backup":
            (
                str(latest_backup)
                if latest_backup
                else None
            ),

        "files_restored":
            [],

        "files_deleted":
            [],

        "files_modified":
            [],

        "execution_status":
            "PREVIEW_ONLY"
    }


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI ROLLBACK SYSTEM")
    print("==========================================")
    print()

    print(
        "[MODE] ROLLBACK PREVIEW"
    )

    print(
        "[SAFETY] NO FILES WILL BE RESTORED."
    )

    print(
        "[SAFETY] NO PROJECT FILES WILL BE MODIFIED."
    )

    print()

    plan = create_rollback_plan()

    print(
        f"[BACKUPS] "
        f"{plan['available_backups']} backup(s) found."
    )

    print()

    if plan["latest_verified_backup"]:

        print(
            "[BACKUP] Latest verified backup:"
        )

        print(
            f"  {plan['latest_verified_backup']}"
        )

    else:

        print(
            "[BACKUP] No verified backup found."
        )

    print()

    if plan["backup_report_verified"]:

        print(
            "[BACKUP] backup.json reports "
            "the backup as VERIFIED."
        )

    else:

        print(
            "[WARNING] backup.json does not "
            "confirm a verified backup."
        )

    print()

    print(
        f"[VERIFICATION] "
        f"{plan['verification_status']}"
    )

    print()

    if plan["rollback_required"]:

        print(
            "[ROLLBACK] Verification failed."
        )

        print(
            "[ROLLBACK] A rollback may be required."
        )

        print(
            "[SAFETY] Automatic rollback remains DISABLED."
        )

    else:

        print(
            "[ROLLBACK] No rollback is currently required."
        )

    print()

    # ======================================
    # SAVE REPORT
    # ======================================

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with ROLLBACK_REPORT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            plan,
            file,
            indent=2
        )

    print(
        f"Rollback report saved: "
        f"{ROLLBACK_REPORT}"
    )

    print()

    print(
        "[FINAL SAFETY DECISION] "
        "PREVIEW ONLY"
    )

    print(
        "[SAFETY] No project files were modified."
    )

    print(
        "[SAFETY] No files were restored."
    )

    print()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

