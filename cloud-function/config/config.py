import os
import json
import base64
from google.cloud import secretmanager


# Function to access openapi key secret from gcp secret manager
def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value

# Set secrets manager variables
project_id = "ra-development"
secret_id = "ra-howler-prototype-openapi-key"
version_id = "latest"

# Set environment variable openai_api_key
OPENAI_API_KEY = access_secret_version(project_id, secret_id, version_id)
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY



# Function to access secret from Google Secret Manager
def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value

# Function to encode secret value from JSON to base64
def encode_to_base64(secret_value):
    encoded_value = base64.b64encode(secret_value.encode("utf-8")).decode("utf-8")
    return encoded_value

# Set secrets manager variables
project_id = "ra-development"
secret_id = "ra-howler-prototype-gcp-service-account-creds"
version_id = "latest"

# Set base64 encoded environment variable gcp_credentials
secret_value_gcp_service_account = access_secret_version(project_id, secret_id, version_id)
GCP_CREDENTIALS = encode_to_base64(secret_value_gcp_service_account)
os.environ["GOOGLE_APPLICATION_CREDENTIALS_BASE64"] = GCP_CREDENTIALS

# Test print secrets
# print(OPENAI_API_KEY)
# print(GCP_CREDENTIALS)
