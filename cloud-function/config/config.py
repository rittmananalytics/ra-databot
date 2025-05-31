import os
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
secret_id = "ra-openai-api-key"
version_id = "latest"

# Set environment variable openai_api_key
OPENAI_API_KEY = access_secret_version(project_id, secret_id, version_id)
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# Set openai model variable
OPEN_AI_MODEL="gpt-4-turbo"
os.environ["OPEN_AI_MODEL"] = OPEN_AI_MODEL

