import subprocess
import sys
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ORCH_DIR.parent


def spawn(title: str, prompt: str, background: bool = True):
    cmd = ["paseo", "run", prompt, "--title", title, "--cwd", str(PROJECT_ROOT)]
    if background:
        cmd.append("--background")
    print("[Orchestrator] Spawning sub-agent:", title)
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: spawn_subagent.py <title> <prompt>")
        sys.exit(1)
    spawn(sys.argv[1], " ".join(sys.argv[2:]))
