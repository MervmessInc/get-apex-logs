import errno
import logging
import os
import pandas as pd
import requests
import sys

from dotenv import load_dotenv
from typing import List, Optional
from simple_salesforce import Salesforce, format_soql

# Constants
SALESFORCE_API_VERSION = "62.0"
LOGS_DIRECTORY = "apexlogs"

# Configure logging
logging.basicConfig(format="%(asctime)s : %(message)s", level=logging.INFO)

# Load environment variables
load_dotenv()


def validate_env_vars() -> None:
    """Validate required environment variables."""
    required_vars = ["SALESFORCE_INSTANCE", "SALESFORCE_TOKEN", "LOG_LENGTH"]
    for var in required_vars:
        if not os.getenv(var):
            logging.error(f"Missing required environment variable: {var}")
            sys.exit(1)


def salesforce_login(creds: List[str]) -> Optional[Salesforce]:
    """Log in to Salesforce using credentials."""
    try:
        sf = Salesforce(
            instance=creds[0],
            session_id=creds[1],
            version=SALESFORCE_API_VERSION,
        )
        sf.is_sandbox()
        logging.info("Successfully logged into Salesforce.")
        return sf
    except Exception as e:
        logging.error(f"Salesforce login failed: {e}")
        return None


def get_apex_logs(sf: Salesforce, length: int) -> pd.DataFrame:
    """Retrieve Apex Logs from Salesforce."""
    query_str = format_soql(
        f"""
        SELECT Id, StartTime, Location, LogLength
        FROM ApexLog
        WHERE LogLength > {length}
        AND StartTime = TODAY
        ORDER BY LogLength DESC
        """
    )
    try:
        result = sf.query(query_str)
        if not result["records"]:
            logging.info("No Apex Logs found.")
            return pd.DataFrame()
        df = pd.DataFrame(result["records"])
        df.drop(["attributes"], axis=1, inplace=True)
        return df
    except Exception as e:
        logging.error(f"Failed to retrieve Apex Logs: {e}")
        return pd.DataFrame()


def download_apex_log(sf: Salesforce, apex_log_id: str) -> Optional[bytes]:
    """Download a specific Apex Log."""
    try:
        base_url = sf.sf_instance
        download_url = f"https://{base_url}/apexdebug/traceDownload.apexp?id={apex_log_id}"
        response = requests.get(download_url, headers=sf.headers)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to download Apex Log {apex_log_id}: {e}")
        return None


def create_logs_directory(directory: str) -> None:
    """Create a directory for storing logs."""
    try:
        os.mkdir(directory)
        logging.info(f"Directory '{directory}' created successfully.")
    except OSError as e:
        if e.errno == errno.EEXIST:
            logging.info(f"Directory '{directory}' already exists.")
        else:
            logging.error(f"Failed to create directory '{directory}': {e}")
            raise


def main():
    validate_env_vars()

    # Salesforce credentials
    sf_credentials = [
        os.getenv("SALESFORCE_INSTANCE"),
        os.getenv("SALESFORCE_TOKEN"),
    ]

    # Log in to Salesforce
    sf = salesforce_login(sf_credentials)
    if not sf:
        logging.error("Exiting due to failed Salesforce login.")
        sys.exit(1)

    # Get Apex Logs
    log_length = int(os.getenv("LOG_LENGTH"))
    df = get_apex_logs(sf, log_length)
    if df.empty:
        logging.info("No Apex Logs to download. Exiting.")
        sys.exit(0)

    logging.info(f"Number of Apex Logs: {len(df)}")

    # Create logs directory
    create_logs_directory(LOGS_DIRECTORY)

    # Download each Apex Log
    for i in range(len(df)):
        apex_log_id = df.loc[i, "Id"]
        apex_log = download_apex_log(sf, apex_log_id)
        if apex_log:
            file_path = os.path.join(LOGS_DIRECTORY, f"apex_log-{apex_log_id}.log")
            with open(file_path, "wb") as f:
                f.write(apex_log)
            logging.info(f"Downloaded Apex Log: {file_path}")

    logging.info("All Apex Logs downloaded successfully.")


if __name__ == "__main__":
    main()
