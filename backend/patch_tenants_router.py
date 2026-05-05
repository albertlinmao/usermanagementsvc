with open("src/api/routers/tenants.py", "r") as f:
    content = f.read()

get_tenant_code = """
from api.deps import get_tenant_context, TenantContext
from uuid import UUID

@router.get("/", response_model=TenantResponse)
async def get_tenant(
    context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db)
):
    \"\"\"Get the current tenant profile based on Edge Gateway context.\"\"\"
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
"""

content += get_tenant_code

with open("src/api/routers/tenants.py", "w") as f:
    f.write(content)
