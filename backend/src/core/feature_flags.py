from core.config import settings


from typing import Optional


class FeatureFlagProvider:
    def is_enabled(self, feature_name: str, context: Optional[dict] = None) -> bool:
        """
        Check if a feature is enabled.
        This is a placeholder interface for an Unleash client.
        """
        # TODO: Integrate Unleash client here
        # Return True for development purposes
        return True


feature_flags = FeatureFlagProvider()
