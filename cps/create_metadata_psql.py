import sys
import os

# Add project root to sys.path and remove the current directory (cps/) from it
# to avoid name collisions (e.g., cps/babel.py shadowing the system babel package)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if script_dir in sys.path:
    sys.path.remove(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import subprocess
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

from cps.utils import get_env_path, get_project_root
from cps import logger, auto_create_threads

log = logger.create()

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv(get_env_path())

DB_USER     = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DATABASENAME_APP")


# ---------------------------
# Auto install pgloader
# ---------------------------
def ensure_pgloader_installed():
    try:
        subprocess.run(["pgloader", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.info("✔ pgloader already installed.")
    except FileNotFoundError:
        log.info("⚠ pgloader not found. Installing...")
        subprocess.run(["sudo", "apt-get", "update", "-y"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "pgloader"])
        log.info("✔ pgloader installed successfully.")

# ---------------------------
# Migration workflow
# ---------------------------
def migrate_sqlite_to_postgres(SQLITE_PATH):
    if not SQLITE_PATH.endswith('.db'):
        SQLITE_PATH = os.path.join(SQLITE_PATH, 'metadata.db')

    # Encode password safely
    encoded_pw = urllib.parse.quote_plus(DB_PASSWORD)
    
    TARGET_PGLOADER_URL = (
        f"postgresql://{DB_USER}:{encoded_pw}@{DB_HOST}:{DB_PORT}/{DB_NAME.lower()}"
    )
    log.info(f"pgloader Target URL  = {TARGET_PGLOADER_URL.replace(encoded_pw, '********')}")

    # Ensure pgloader installed
    ensure_pgloader_installed()
    
    # -------------------------------------
    # Run pgloader migration
    # -------------------------------------
    log.info("\nRunning migration using pgloader...\n")

    command = [
        "pgloader",
        f"sqlite:///{SQLITE_PATH}",
        TARGET_PGLOADER_URL
    ]
    log.info(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    log.info("=========== PGLOADER OUTPUT ===========")
    log.info(result.stdout)
    log.info("=========== PGLOADER ERRORS ===========")
    log.info(result.stderr)

    if result.returncode != 0:
        error_msg = f"pgloader failed with return code {result.returncode}. Stderr: {result.stderr}"
        log.error(f"⚠ {error_msg}")
        raise Exception(error_msg)

    log.info("✔ Migration completed successfully.")
    auto_create_threads.create_threads()

# ---------------------------
# Main entry
# ---------------------------
# default path
SQLITE_PATH = os.path.join(get_project_root(), 'library/metadata.db')

if __name__ == "__main__":
    migrate_sqlite_to_postgres(SQLITE_PATH)
