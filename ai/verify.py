from pathlib import Path
import json
import subprocess
import shutil
from datetime import datetime

# ==========================================
# EAST SMP AI VERIFICATION SYSTEM
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = PROJECT_ROOT / "reports"
SCANNER_FILE = REPORTS_DIR / "scanner.json"
VERIFICATION_FILE = REPORTS_DIR / "verification.json"


# ==========================================
# RUN COMMAND
# ==========================================

def run_command(command):
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            shell=False
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except FileNotFoundError as error:

        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(error)
        }

    except OSError as error:

        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(error)
        }


# ==========================================
# FIND NPM
# ==========================================

def find_npm():

    # Windows normally uses npm.cmd
    npm_cmd = shutil.which("npm.cmd")

    if npm_cmd:
        return npm_cmd

    # Fallback for other systems
    npm_cmd = shutil.which("npm")

    if npm_cmd:
        return npm_cmd

    return None


# ==========================================
# LOAD SCANNER REPORT
# ==========================================

def load_scanner_report():

    if not SCANNER_FILE.exists():

        print("[ERROR] scanner.json was not found.")
        print(f"Expected: {SCANNER_FILE}")

        return None

    try:

        with SCANNER_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError as error:

        print("[ERROR] scanner.json contains invalid JSON.")
        print(error)

        return None

    except OSError as error:

        print("[ERROR] Could not read scanner.json.")
        print(error)

        return None


# ==========================================
# VERIFY SCANNER
# ==========================================

def verify_scanner():

    print()
    print("[VERIFY] Running project scanner...")
    print()

    scanner_path = PROJECT_ROOT / "tools" / "ProjectScanner.js"

    if not scanner_path.exists():

        print("[FAIL] ProjectScanner.js was not found.")

        return {
            "passed": False,
            "tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }

    result = run_command(
        [
            "node",
            str(scanner_path)
        ]
    )

    if not result["success"]:

        print("[FAIL] Project scanner failed.")

        if result["stderr"]:
            print(result["stderr"])

        return {
            "passed": False,
            "tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }

    report = load_scanner_report()

    if report is None:

        return {
            "passed": False,
            "tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }

    total = len(report)

    passed = sum(
        1
        for item in report
        if item.get("passed") is True
    )

    failed = total - passed

    print(f"Tests: {passed}/{total}")

    if failed == 0:

        print("[PASS] All scanner tests passed.")

    else:

        print(f"[FAIL] {failed} scanner tests failed.")

    return {
        "passed": failed == 0,
        "tests": total,
        "passed_tests": passed,
        "failed_tests": failed
    }


# ==========================================
# VERIFY ASTRO BUILD
# ==========================================

def verify_build():

    print()
    print("[VERIFY] Running Astro build...")
    print()

    npm = find_npm()

    if npm is None:

        print("[FAIL] npm executable could not be found.")

        return {
            "passed": False,
            "error": "npm executable not found"
        }

    print(f"[VERIFY] npm: {npm}")

    result = run_command(
        [
            npm,
            "run",
            "build"
        ]
    )

    if result["success"]:

        print()
        print("[PASS] Astro build completed successfully.")

        return {
            "passed": True,
            "error": None
        }

    print()
    print("[FAIL] Astro build failed.")

    if result["stderr"]:

        print()
        print(result["stderr"])

    return {
        "passed": False,
        "error": result["stderr"]
    }


# ==========================================
# VERIFY DIST
# ==========================================

def verify_dist():

    print()
    print("[VERIFY] Checking build output...")
    print()

    dist = PROJECT_ROOT / "dist"

    if not dist.exists():

        print("[FAIL] dist directory does not exist.")

        return False

    index = dist / "index.html"

    if not index.exists():

        print("[FAIL] dist/index.html does not exist.")

        return False

    print("[PASS] dist/index.html exists.")

    return True


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("==========================================")
    print(" EAST SMP AI VERIFICATION SYSTEM")
    print("==========================================")
    print()

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    scanner_result = verify_scanner()

    build_result = verify_build()

    dist_result = verify_dist()

    final_passed = (
        scanner_result["passed"]
        and build_result["passed"]
        and dist_result
    )

    print()
    print("==========================================")

    if final_passed:

        print(" FINAL VERIFICATION: PASSED")
        print("==========================================")
        print()
        print("[SAFETY] Project verification successful.")
        print("[SAFETY] No rollback required.")

    else:

        print(" FINAL VERIFICATION: FAILED")
        print("==========================================")
        print()
        print("[SAFETY] Project verification failed.")
        print("[ROLLBACK] A rollback should be considered.")
        print("[SAFETY] Automatic rollback is disabled.")

    verification_report = {

        "timestamp": datetime.now().isoformat(),

        "final_verification": (
            "PASSED"
            if final_passed
            else "FAILED"
        ),

        "scanner": scanner_result,

        "astro_build": build_result,

        "dist_verification": {
            "passed": dist_result
        },

        "automatic_rollback": False
    }

    with VERIFICATION_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            verification_report,
            file,
            indent=2
        )

    print()
    print(
        f"Verification report saved: {VERIFICATION_FILE}"
    )


if __name__ == "__main__":
    main()
