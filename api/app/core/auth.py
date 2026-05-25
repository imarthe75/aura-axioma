import jwt
import logging
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.AUTHENTIK_URL}/application/o/token/",
    auto_error=False,
)

_jwks_client = PyJWKClient(
    f"{settings.AUTHENTIK_INTERNAL_URL}/application/o/{settings.AUTHENTIK_CLIENT_ID}/jwks/"
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if not token:
        logging.warning("[axioma] No token received in Authorization header")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Clean token if it has Bearer prefix or double quotes
    token = token.replace('Bearer ', '').replace('"', '').strip()
    
    logging.info(f"[axioma] Received token value: '{token[:20]}...' (length: {len(token)})")
    
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.AUTHENTIK_CLIENT_ID,
            options={"verify_exp": True},
        )
        return {
            "email": payload.get("email") or payload.get("sub"),
            "username": payload.get("preferred_username"),
            "groups": payload.get("groups", []),
        }
    except Exception as e:
        logging.warning(f"[axioma] JWT validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
