
from pathlib import Path
from datetime import datetime
import shutil
import json

# ==========================================
# EAST SMP AI BACKUP SYSTEM
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKUP_ROOT = PROJECT_ROOT / "backups"
REPORT_ROOT = PROJECT_ROOT / "reports"

BACKUP_REPORT = REPORT_ROOT / "backup.json"


# ==========================================
# FILES / FOLDERS TO IGNORE
# ==========================================

IGNORE_NAMES = {
    ".git",
    "node_modules",
    ".astro",
    "dist",
    "__pycache__",
    "backups"
}


# ==========================================
# CHECK WHETHER PATH SHOULD BE IGNORED
# ==========================================

def should_ignore(path):

    return any(
        part in IGNORE_NAMES
        for part in path.relative_to(PROJECT_ROOT).parts
    )


# ==========================================
# CREATE BACKUP
# ==========================================

def create_backup():

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_directory = (
        BACKUP_ROOT / timestamp
    )

    print()
    print("==========================================")
    print(" EAST SMP AI BACKUP SYSTEM")
    print("==========================================")
    print()

    print(
        f"Backup location: {backup_directory}"
    )

    print()

    # --------------------------------------
    # CREATE BACKUP DIRECTORY
    # --------------------------------------

    try:

        backup_directory.mkdir(
            parents=True,
            exist_ok=False
        )

    except OSError as error:

        print(
            "[BACKUP FAILED] Could not create backup directory."
        )

        print(error)

        return None

    copied_files = 0
    copied_directories = 0

    # --------------------------------------
    # COPY PROJECT
    # --------------------------------------

    try:

        for source in PROJECT_ROOT.rglob("*"):

            if should_ignore(source):
                continue

            relative_path = source.relative_to(
                PROJECT_ROOT
            )

            destination = (
                backup_directory / relative_path
            )

            if source.is_dir():

                destination.mkdir(
                    parents=True,
                    exist_ok=True
                )

                copied_directories += 1

            elif source.is_file():

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.copy2(
                    source,
                    destination
                )

                copied_files += 1

    except Exception as error:

        print()
        print(
            "[BACKUP FAILED] Error while copying project."
        )

        print(error)

        # Remove incomplete backup

        try:

            shutil.rmtree(
                backup_directory
            )

        except OSError:
            pass

        return None

    # --------------------------------------
    # VERIFY BACKUP
    # --------------------------------------

    print(
        f"Files copied: {copied_files}"
    )

    print(
        f"Directories copied: {copied_directories}"
    )

    print()
    print("Verifying backup...")

    if not backup_directory.exists():

        print(
            "[BACKUP FAILED] Backup directory does not exist."
        )

        return None

    if copied_files == 0:

        print(
            "[BACKUP FAILED] No files were copied."
        )

        return None

    # --------------------------------------
    # VERIFY IMPORTANT PROJECT FILES
    # --------------------------------------

    important_files = [
        "package.json",
        "astro.config.mjs"
    ]

    missing_files = []

    for relative_file in important_files:

        backup_file = (
            backup_directory / relative_file
        )

        if not backup_file.exists():

            missing_files.append(
                relative_file
            )

    if missing_files:

        print(
            "[BACKUP FAILED] Important files are missing."
        )

        for file in missing_files:

            print(
                f"- {file}"
            )

        return None

    # --------------------------------------
    # CREATE BACKUP REPORT
    # --------------------------------------

    report = {

        "backup_successful": True,

        "timestamp": timestamp,

        "backup_directory":
            str(backup_directory),

        "files_copied":
            copied_files,

        "directories_copied":
            copied_directories,

        "verified": True,

        "important_files_verified":
            important_files,

        "missing_important_files":
            missing_files

    }

    REPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        with BACKUP_REPORT.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=2
            )

    except OSError as error:

        print(
            "[BACKUP FAILED] Could not save backup report."
        )

        print(error)

        return None

    # --------------------------------------
    # FINAL RESULT
    # --------------------------------------

    print()
    print("==========================================")
    print(" BACKUP SUCCESSFUL")
    print("==========================================")
    print()

    print(
        f"Backup: {backup_directory}"
    )

    print(
        f"Files: {copied_files}"
    )

    print(
        f"Verified: YES"
    )

    print()

    print(
        f"Report saved: {BACKUP_REPORT}"
    )

    print()

    return report


# ==========================================
# MAIN
# ==========================================

def main():

    result = create_backup()

    if result is None:

        print()
        print(
            "[SAFETY] Changes must NOT be allowed."
        )

        return

    print(
        "[SAFETY] Verified backup exists."
    )

    print(
        "[SAFETY] Project is protected by this backup."
    )


if __name__ == "__main__":

    main()