from fastapi import Header, HTTPException, status
from core.config import settings


def verify_gateway_psk(
    x_internal_secret: str = Header(..., alias="X-Internal-Secret"),
) -> bool:
    """
    Dependency to verify that the request came from the trusted Edge Gateway.
    """
    if x_internal_secret != settings.GATEWAY_PSK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gateway authentication failed.",
        )
    return True
