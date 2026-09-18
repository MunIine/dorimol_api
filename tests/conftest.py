import pytest

@pytest.fixture
def test_user():
    return {
        "uid": "test_user_uid",
        "role": "user",
        "onboarding_completed": True,
        "phone_number": "+37378877788",
    }