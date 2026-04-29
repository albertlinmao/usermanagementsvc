from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from core.security import verify_gateway_psk
from models.schemas import TenantRegistrationRequest, TenantResponse
from services.onboarding_service import OnboardingService

router = APIRouter()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(
    request: TenantRegistrationRequest,
    session: AsyncSession = Depends(get_db),
    _=Depends(verify_gateway_psk),
):
    """
    Registers a new tenant, provisions a Supabase Auth user, encrypts PII,
    and sets up the isolated tenant boundary. Bypasses JWT validation, relying
    on the pre-shared key from the Edge Gateway for internet-facing security.
    """
    try:
        service = OnboardingService(session)
        response = await service.register_tenant(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during tenant registration: {str(e)}",
        )
