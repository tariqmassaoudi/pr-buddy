import os
import dotenv

dotenv.load_dotenv()

organization_url = os.getenv("AZURE_ORGANIZATION_URL")
personal_access_token = os.getenv("AZURE_PERSONAL_ACCESS_TOKEN")

AZURE_CONFIG = {
    "api_version": os.getenv("AZURE_API_VERSION"),
    "azure_endpoint": os.getenv("AZURE_ENDPOINT"),
    "azure_deployment": os.getenv("AZURE_DEPLOYMENT"),
    "model": os.getenv("AZURE_MODEL"),
    "openai_api_key": os.getenv("AZURE_API_KEY"),
}
