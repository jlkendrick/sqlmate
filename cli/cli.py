# sqlmate/cli/cli.py
import argparse
import os
import secrets
import subprocess
import getpass
from pathlib import Path
from importlib.resources import files

TEMPLATE_DIR = Path(__file__).parent / "templates"
docker_compose_file = files("cli.docker") / "docker-compose.yaml"
secrets_file = os.path.join(os.path.expanduser("~"), ".sqlmate", "secrets.env")

def generate_defaults() -> dict:
    """Generate default values for database connection credentials."""

    defaults = {
        "PORT": 5432,
        "DB_HOST": "localhost",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "sqlmate",
        "JWT_SECRET": secrets.token_urlsafe(16),
    }

    # If the secrets.env file already exists, read the existing values to be used as defaults
    if os.path.exists(secrets_file):
        with open(secrets_file, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                if key in defaults:
                    defaults[key] = value.strip("'\"")

    return defaults

def prompt_for_credentials(defaults: dict) -> dict:
    """Prompt the user for database connection credentials."""
    print("📝 Please enter your database connection details:")
    
    # Collect credentials with defaults
    credentials = {}
    credentials["PORT"] = input(f"API Port [{defaults['PORT']}]: ") or defaults["PORT"]
    credentials["DB_HOST"] = input(f"Database Host [{defaults['DB_HOST']}]: ") or defaults["DB_HOST"]
    credentials["DB_USER"] = input(f"Database User [{defaults['DB_USER']}]: ") or defaults["DB_USER"]
    credentials["DB_PASSWORD"] = getpass.getpass("Database Password: ")
    credentials["DB_NAME"] = input(f"Database Name [{defaults['DB_NAME']}]: ") or defaults["DB_NAME"]
    credentials["JWT_SECRET"] = defaults["JWT_SECRET"]
    
    return credentials

def create_env_file(credentials, target_path):
    """Create a secrets.env file with the provided credentials."""
    env_content = "\n".join([f"{key}='{value}'" for key, value in credentials.items()])
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Write the env file
    with open(target_path, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created configuration file at {target_path}")

def init():
    print("🔧 Initializing SQLMate project...")
    
    # Define the path for the env file in user's home directory
    env_file_path = os.path.join(
        os.path.expanduser('~'),
        '.sqlmate',
        'secrets.env'
    )

    defaults = generate_defaults()
    
    # Prompt for credentials and create env file
    credentials = prompt_for_credentials(defaults)
    create_env_file(credentials, env_file_path)
    
    print("✅ Project initialized. Run `sqlmate run` to start.")

def run():
    print("🚀 Starting SQLMate with Docker...")

    # Check if the Docker daemon is running
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ Docker daemon is not running. Please start Docker and try again.")
        return
    except FileNotFoundError:
        print("❌ Docker is not installed. Please install Docker and try again.")
        return
    # Check if Docker Compose is installed
    try:
        subprocess.run(["docker-compose", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ Docker Compose is not installed. Please install Docker Compose and try again.")
        return
    except FileNotFoundError:
        print("❌ Docker Compose is not installed. Please install Docker Compose and try again.")
        return
    
    # Check if 'sqlmate init' has been run (i.e., if the env file exists)
    env_file_path = os.path.join(
        os.path.expanduser('~'),
        '.sqlmate',
        'secrets.env'
    )
    if not os.path.exists(env_file_path):
        print("❌ Configuration file not found. Please run `sqlmate init` first.")
        return
    

    subprocess.run(["docker", "compose", "-f", str(docker_compose_file), "up", "--build"], check=True)

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
