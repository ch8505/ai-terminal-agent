import subprocess
import os
from dataclasses import dataclass

# ===================================================================
# CommandResult — מבנה הנתונים שמחזירים מכל הרצה
# ===================================================================
# dataclass יוצרת אוטומטית __init__, __repr__ וכו' — חוסכת boilerplate
@dataclass
class CommandResult:
    stdout: str      # פלט רגיל
    stderr: str      # פלט שגיאות
    exit_code: int   # 0 = הצלחה, כל מספר אחר = כישלון


DOCKER_IMAGE = "ubuntu:22.04"
TIMEOUT_SECONDS = 15
WORKDIR = "/workspace"


def run_in_sandbox(command: str) -> CommandResult:
    """
    מריצה פקודת shell בתוך Docker container מבודד ומאובטח.
    כל הרצה = container חדש ונקי. אין state בין הרצות.
    """

    if not command or command.startswith("ERROR"):
        return CommandResult(stdout="", stderr="No valid command to run.", exit_code=1)

    # ניצור את תיקיית workdir אם לא קיימת
    os.makedirs("workdir", exist_ok=True)

    container_cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--pids-limit", "64",
        "--memory", "128m",
        "-v", f"{os.getcwd()}/workdir:{WORKDIR}:rw",
        "--workdir", WORKDIR,
        "--user", "1000:1000",
        DOCKER_IMAGE,
        "bash", "-c", f"timeout {TIMEOUT_SECONDS} {command}",
    ]

    try:
        result = subprocess.run(
            container_cmd,
            capture_output=True,       # לוכד stdout/stderr בנפרד, לא מדפיס לטרמינל
            text=True,                 # מחזיר str ולא bytes גולמיים
            timeout=TIMEOUT_SECONDS + 5,
        )

        return CommandResult(
            stdout=result.stdout.strip() or "(no output)",
            stderr=result.stderr.strip() or "(no errors)",
            exit_code=result.returncode,
        )

    except subprocess.TimeoutExpired:
        return CommandResult(
            stdout="",
            stderr=f"Timed out after {TIMEOUT_SECONDS}s.",
            exit_code=124,  # 124 הוא exit code סטנדרטי ל-timeout ב-Linux
        )

    except FileNotFoundError:
        return CommandResult(
            stdout="",
            stderr="Docker is not installed or not running.\nInstall: https://docs.docker.com/get-docker/",
            exit_code=1,
        )

    except Exception as e:
        return CommandResult(stdout="", stderr=str(e), exit_code=1)


# ===================================================================
# הרצה ישירה לבדיקה: python sandbox.py "ls -la"
# ===================================================================
if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ls -la"
    print(f"Running: {cmd}")
    result = run_in_sandbox(cmd)
    print(f"EXIT CODE : {result.exit_code}")
    print(f"STDOUT    :\n{result.stdout}")
    print(f"STDERR    :\n{result.stderr}")