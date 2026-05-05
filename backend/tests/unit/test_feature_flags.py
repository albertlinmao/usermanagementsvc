import pytest
from core.feature_flags import FeatureFlagProvider, feature_flags

def test_feature_flag_provider():
    # Test the class instance directly
    provider = FeatureFlagProvider()
    assert provider.is_enabled("some_feature") is True
    assert provider.is_enabled("some_other_feature", context={"user_id": "123"}) is True

def test_feature_flags_singleton():
    # Test the global instance
    assert feature_flags.is_enabled("any_feature") is True
