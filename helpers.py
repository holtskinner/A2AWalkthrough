import os

import google.auth
import google.auth.credentials
import google.auth.transport.requests
from dotenv import load_dotenv
from google.auth import impersonated_credentials
from google.oauth2 import service_account


def authenticate(
    location: str | None = None,
) -> tuple[google.auth.credentials.Credentials, str]:
    load_dotenv(override=True)

    # 1. Locate the JSON key file
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # SAFETY CHECK: Ensure the file actually exists
    if not key_path or not os.path.exists(key_path):
        # Fallback: Try to look in the current directory if env var is missing
        if os.path.exists("credentials.json"):
            key_path = "credentials.json"
        elif os.path.exists("../credentials.json"):
            key_path = "../credentials.json"
        else:
            raise ValueError(
                "Could not find credentials.json or GOOGLE_APPLICATION_CREDENTIALS env var."
            )

    # 2. Load the file EXPLICITLY with scopes
    source_credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # 3. Create the HTTP Request object
    request = google.auth.transport.requests.Request()

    # 4. Refresh the source credential (The 1-hour token)
    source_credentials.refresh(request)

    # 5. Create Impersonated Credentials (The 2-hour token)
    target_principal = source_credentials.service_account_email

    credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_principal,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        lifetime=7200,  # 2 Hours
    )

    # 6. Refresh to get the final token
    credentials.refresh(request)

    # Set Env Vars
    os.environ["GOOGLE_CLOUD_PROJECT"] = source_credentials.project_id
    if location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = location

    return credentials, source_credentials.project_id
