# sqlmate/cli/cli.py
import argparse
import shutil
import subprocess
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"

def init():
    print("🔧 Initializing SQLMate project...")

    dest = Path.cwd()
    for file in TEMPLATE_DIR.iterdir():
        shutil.copy(file, dest / file.name)

    print("✅ Project initialized. Run `sqlmate run` to start.")

def run():
    print("🚀 Starting SQLMate with Docker...")
    subprocess.run(["docker-compose", "up"], check=True)

def main():
    parser = argparse.ArgumentParser(prog="sqlmate")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize the project")
    subparsers.add_parser("run", help="Run the Docker app")

    args = parser.parse_args()
    if args.command == "init":
        init()
    elif args.command == "run":
        run()
    else:
        parser.print_help()
