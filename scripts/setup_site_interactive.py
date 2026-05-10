#!/usr/bin/env python3
r"""Friendly, cross-platform setup and deployment guide for the aggregator site.

Run from the repository root with either:
    python scripts/setup_site_interactive.py
or:
    py scripts\setup_site_interactive.py
"""

from __future__ import annotations

import argparse
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATTRIBUTES = "brand,model,year,price,cc,mileage,features,owners,km_run"


def is_windows() -> bool:
    return platform.system().lower().startswith("win")


def venv_python() -> Path:
    if is_windows():
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def venv_pip() -> Path:
    if is_windows():
        return ROOT / ".venv" / "Scripts" / "pip.exe"
    return ROOT / ".venv" / "bin" / "pip"


def quote_command(parts: list[str | Path]) -> str:
    text_parts = [str(part) for part in parts]
    if is_windows():
        return subprocess.list2cmdline(text_parts)
    return " ".join(shlex.quote(part) for part in text_parts)


def pause(message: str = "Press Enter after you have read this step...") -> None:
    input(f"\n{message}")


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    default_text = "Y/n" if default else "y/N"
    while True:
        value = input(f"{prompt} ({default_text}): ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Please type yes or no.")


def run_step(parts: list[str | Path], description: str) -> None:
    print(f"\nSTEP: {description}")
    print(f"Running: {quote_command(parts)}")
    subprocess.run([str(part) for part in parts], cwd=ROOT, check=True)
    print("Done.")


def print_manual_command(parts: list[str | Path], explanation: str) -> None:
    print(f"\n{explanation}")
    print(f"    {quote_command(parts)}")


def ensure_venv() -> None:
    python_path = venv_python()
    if python_path.exists():
        print(f"Found existing virtual environment at {ROOT / '.venv'}.")
        return
    run_step([sys.executable, "-m", "venv", ".venv"], "Create a private Python environment for this site")


def install_requirements() -> None:
    run_step([venv_python(), "-m", "pip", "install", "--upgrade", "pip"], "Update pip inside the private environment")
    run_step([venv_pip(), "install", "-r", "requirements.txt"], "Install the site software packages")


def initialize_site(product: str, attributes: str) -> None:
    run_step(
        [
            venv_python(),
            "scripts/setup_aggregator.py",
            "--product",
            product,
            "--attributes",
            attributes,
            "--with-frontend",
        ],
        "Create the first product category and database tables",
    )


def local_setup() -> None:
    print("\nLOCAL SITE SETUP")
    print("This prepares the website on this computer. It is safe to run more than once.")
    product = ask("What kind of listings will this site collect? Use one simple word, for example bikes or cameras", "bikes")
    attributes = ask("Which listing details should be searchable? Separate words with commas", DEFAULT_ATTRIBUTES)

    ensure_venv()
    install_requirements()
    initialize_site(product, attributes)

    print("\nYour local site is ready.")
    print_manual_command([venv_python(), "-m", "uvicorn", "app.main:app", "--reload"], "To start it later, run this command from the project folder:")
    print("Then open http://127.0.0.1:8000/ in your web browser.")

    if ask_yes_no("Start the local website now", True):
        print("\nStarting the site. Leave this window open. Press Ctrl+C to stop it.")
        subprocess.run([str(venv_python()), "-m", "uvicorn", "app.main:app", "--reload"], cwd=ROOT, check=False)


def deployment_common_intro(provider: str) -> None:
    print(f"\n{provider.upper()} DEPLOYMENT WALKTHROUGH")
    print("This script explains each cloud step and waits for you to complete it.")
    print("You will need a cloud account, a billing method, Docker Desktop, and Git installed.")
    print("For a serious live site, create a managed PostgreSQL database and set DATABASE_URL.")
    pause()

    print("\nFirst, make sure the site runs locally before deploying.")
    print_manual_command([venv_python(), "-m", "uvicorn", "app.main:app", "--reload"], "If you have not tested locally yet, run:")
    pause("Press Enter after the local site opens correctly, or after you decide to continue anyway...")

    print("\nNext, put your code in Git so the cloud service can build it.")
    print_manual_command(["git", "status"], "Check your files with:")
    print_manual_command(["git", "add", "."], "If needed, add changed files with:")
    print_manual_command(["git", "commit", "-m", "Prepare deployment"], "If needed, save your changes with:")
    pause("Press Enter after your code is saved in Git...")


def aws_walkthrough() -> None:
    deployment_common_intro("AWS")
    print("\nRecommended beginner AWS target: AWS App Runner.")
    print("1. Open the AWS Console and search for 'App Runner'.")
    print("2. Choose 'Create service'.")
    print("3. Choose a source: either your GitHub repository or a container image.")
    print("4. If using source code, let App Runner build from the Dockerfile in this project.")
    print("5. Set port to 8000 if AWS asks for a port.")
    print("6. Add environment variable DATABASE_URL only if you created a managed database.")
    print("7. Click create/deploy and wait for the service URL.")
    pause("Press Enter after AWS gives you a public service URL...")
    print("\nOpen the URL AWS shows. Add /docs to see the API documentation.")


def gcp_walkthrough() -> None:
    deployment_common_intro("Google Cloud")
    print("\nRecommended beginner GCP target: Cloud Run.")
    print("1. Open Google Cloud Console and create or select a project.")
    print("2. Enable Cloud Run and Artifact Registry if Google asks.")
    print("3. Open Cloud Run and choose 'Deploy container' or 'Continuously deploy from source'.")
    print("4. Select this repository. Google can build it using the Dockerfile.")
    print("5. Allow unauthenticated access if this is a public website.")
    print("6. Set container port to 8000 if asked.")
    print("7. Add DATABASE_URL only if you created Cloud SQL or another PostgreSQL database.")
    print("8. Deploy and wait for the Cloud Run URL.")
    pause("Press Enter after GCP gives you a public service URL...")
    print("\nOpen the URL GCP shows. Add /docs to see the API documentation.")


def azure_walkthrough() -> None:
    deployment_common_intro("Azure")
    print("\nRecommended beginner Azure target: Azure Container Apps.")
    print("1. Open the Azure Portal and create a Resource Group.")
    print("2. Search for 'Container Apps' and choose 'Create'.")
    print("3. Use the Dockerfile in this repository as the application image source, or connect GitHub Actions.")
    print("4. Set ingress to external/public so visitors can open the site.")
    print("5. Set target port to 8000.")
    print("6. Add DATABASE_URL only if you created Azure Database for PostgreSQL.")
    print("7. Create the app and wait for Azure to show an Application URL.")
    pause("Press Enter after Azure gives you a public application URL...")
    print("\nOpen the URL Azure shows. Add /docs to see the API documentation.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Friendly interactive setup for the aggregator website.")
    parser.add_argument("--local-only", action="store_true", help="Run only the local computer setup questions.")
    args = parser.parse_args()

    os.chdir(ROOT)
    print("Aggregator Website Setup Helper")
    print("================================")
    print(f"Project folder: {ROOT}")
    print("This helper works in macOS/Linux bash, Windows Command Prompt, and PowerShell.")

    if args.local_only:
        local_setup()
        return

    while True:
        print("\nWhat would you like to do?")
        print("1. Set up and run the site on this computer")
        print("2. Walk me through AWS deployment")
        print("3. Walk me through Google Cloud deployment")
        print("4. Walk me through Azure deployment")
        print("5. Quit")
        choice = ask("Type a number", "1")
        if choice == "1":
            local_setup()
        elif choice == "2":
            aws_walkthrough()
        elif choice == "3":
            gcp_walkthrough()
        elif choice == "4":
            azure_walkthrough()
        elif choice == "5":
            print("Goodbye.")
            return
        else:
            print("Please choose 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()
