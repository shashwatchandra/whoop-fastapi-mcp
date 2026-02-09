import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    session_secret: str = os.getenv("SESSION_SECRET", "change_me")
    whoop_client_id: str = os.getenv("WHOOP_CLIENT_ID", "")
    whoop_client_secret: str = os.getenv("WHOOP_CLIENT_SECRET", "")
    whoop_authorize_url: str = os.getenv("WHOOP_AUTH_URL", "https://api.prod.whoop.com/oauth/oauth2/auth")
    whoop_token_url: str = os.getenv("WHOOP_TOKEN_URL", "https://api.prod.whoop.com/oauth/oauth2/token")
    whoop_api_base: str = os.getenv("WHOOP_API_BASE", "https://api.prod.whoop.com")
    whoop_redirect_uri: str = os.getenv("WHOOP_REDIRECT_URI", "")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "")

    # Combined scopes: restrict to the minimum you actually use
    scopes: str = " ".join([
        "read:profile",
        "read:body_measurement",
        "read:cycles",
        "read:workout",
        "read:sleep",
        "read:recovery"
    ])

settings = Settings()
