from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from core.security import verify_gateway_psk
from models.schemas import TenantRegistrationRequest, TenantResponse
from services.onboarding_service import OnboardingService
from core.feature_flags import feature_flags

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
    if not feature_flags.is_enabled("tenant-onboarding"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Tenant onboarding feature is not currently enabled.",
        )

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


from api.deps import get_tenant_context, TenantContext
from uuid import UUID


@router.get("/", response_model=TenantResponse)
async def get_tenant(
    context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db),
):
    """Get the current tenant profile based on Edge Gateway context."""
    try:
        service = OnboardingService(session)
        response = await service.get_tenant(UUID(context.tenant_id))
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
