from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_settings():
    """테스트에서 사용할 설정 모의"""
    with patch("src.core.config.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.environment = "test"
        mock_settings.openai_api_key = "dummy_key_for_test"
        mock_settings.openai_model = "gpt-4-turbo"
        mock_settings.openai_max_tokens = 4000
        mock_settings.internal_api_url = "http://test.example.com"
        mock_settings.internal_api_key = "dummy_internal_key_for_test"
        yield mock_settings
