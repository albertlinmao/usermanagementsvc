with open("src/services/onboarding_service.py", "r") as f:
    content = f.read()

get_tenant_code = """
    async def get_tenant(self, tenant_id: UUID) -> TenantResponse:
        repo = TenantRepository(self.session)
        tenant_data = await repo.get_tenant(tenant_id)
        if not tenant_data:
            raise ValueError(f"Tenant not found: {tenant_id}")
            
        return TenantResponse(
            id=tenant_data["id"],
            name=tenant_data["name"],
            status=tenant_data["status"]
        )
"""

content += get_tenant_code

with open("src/services/onboarding_service.py", "w") as f:
    f.write(content)
