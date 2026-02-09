import secrets
import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from .config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()
oauth = OAuth()
oauth.register(
    name="whoop",
    client_id=settings.whoop_client_id,
    client_secret=settings.whoop_client_secret,
    access_token_url=settings.whoop_token_url,
    authorize_url=settings.whoop_authorize_url,
    api_base_url=settings.whoop_api_base,
    client_kwargs={"scope": settings.scopes},
    token_endpoint_auth_method="client_secret_post",
)

def add_session_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

@router.get("/login")
async def login(request: Request):
    logger.info("=== LOGIN ENDPOINT CALLED ===")
    try:
        if not settings.whoop_redirect_uri:
            # If PUBLIC_BASE_URL is set, build redirect automatically
            if settings.public_base_url:
                # No trailing slash
                base = settings.public_base_url.rstrip('/')
                request.app.state.whoop_redirect_uri = f"{base}/callback"
            else:
                raise HTTPException(500, "WHOOP_REDIRECT_URI not configured")
        state = secrets.token_urlsafe(24)
        request.session["oauth_state"] = state
        redirect_uri = getattr(request.app.state, 'whoop_redirect_uri', settings.whoop_redirect_uri)
        logger.info(f"redirect_uri: {redirect_uri}, state: {state}")
        return await oauth.whoop.authorize_redirect(
            request,
            redirect_uri=redirect_uri,
            state=state
        )
    except Exception as e:
        logger.exception(f"Error in login: {e}")
        raise

@router.get("/callback")
async def callback(request: Request):
    logger.info("=== CALLBACK RECEIVED ===")
    logger.info(f"Query params: {request.query_params}")
    logger.info(f"Session: {dict(request.session)}")
    try:
        state = request.query_params.get("state")
        logger.info(f"State from query: {state}")
        logger.info(f"State from session: {request.session.get('oauth_state')}")
        
        if not state or state != request.session.get("oauth_state"):
            logger.error("State mismatch!")
            raise HTTPException(400, "Invalid state")
        
        # Ensure redirect_uri matches what was sent in login
        redirect_uri = getattr(request.app.state, 'whoop_redirect_uri', settings.whoop_redirect_uri)
        if not redirect_uri and settings.public_base_url:
            base = settings.public_base_url.rstrip('/')
            redirect_uri = f"{base}/callback"
        
        logger.info(f"Using redirect_uri: {redirect_uri}")
        logger.info("About to exchange token...")
        
        token = await oauth.whoop.authorize_access_token(request, redirect_uri=redirect_uri)
        logger.info(f"Token received: {token}")
        
        request.session["token"] = token
        logger.info("Token stored in session, redirecting to /me")
        return RedirectResponse(url="/me")
    except Exception as e:
        logger.exception(f"Error in callback: {e}")
        raise HTTPException(500, f"OAuth callback failed: {str(e)}")

def get_session_token(request: Request) -> Optional[dict]:
    return request.session.get("token")
