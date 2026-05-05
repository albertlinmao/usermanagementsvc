import pytest
from db.session import get_db

@pytest.mark.asyncio
async def test_get_db():
    # It yields an AsyncSession
    async for session in get_db():
        assert session is not None
        # We don't want to actually connect, but just creating it is fine since it's lazy
