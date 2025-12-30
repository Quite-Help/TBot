"""Tests for model classes."""
import pytest

from app.services.core.model import (
    AliasResponse,
    CounselorInfo,
    CounselorResponse,
    CounselorsResponse,
    GroupLinkResponse,
    ResolveGroupResponse,
)
from app.services.taccount.model import CreateSessionResponse


class TestCounselorInfo:
    """Tests for CounselorInfo model."""

    def test_counselor_info_creation(self):
        """Test creating a CounselorInfo instance."""
        counselor = CounselorInfo(id="1", name="John Doe")
        assert counselor.id == "1"
        assert counselor.name == "John Doe"

    def test_counselor_info_validation(self):
        """Test CounselorInfo validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            CounselorInfo(id="1")  # Missing name


class TestAliasResponse:
    """Tests for AliasResponse model."""

    def test_alias_response_creation(self):
        """Test creating an AliasResponse instance."""
        response = AliasResponse(alias="test_alias")
        assert response.alias == "test_alias"

    def test_alias_response_ignores_extra_fields(self):
        """Test that AliasResponse ignores extra fields."""
        response = AliasResponse(alias="test_alias", extra_field="ignored")
        assert response.alias == "test_alias"
        assert not hasattr(response, "extra_field")


class TestCounselorsResponse:
    """Tests for CounselorsResponse model."""

    def test_counselors_response_creation(self):
        """Test creating a CounselorsResponse instance."""
        counselors = [
            CounselorInfo(id="1", name="John"),
            CounselorInfo(id="2", name="Jane"),
        ]
        response = CounselorsResponse(counselors=counselors)
        assert len(response.counselors) == 2
        assert response.counselors[0].name == "John"
        assert response.counselors[1].name == "Jane"


class TestCounselorResponse:
    """Tests for CounselorResponse model."""

    def test_counselor_response_creation(self):
        """Test creating a CounselorResponse instance."""
        response = CounselorResponse(id="1", name="John Doe", bio="Test bio")
        assert response.id == "1"
        assert response.name == "John Doe"
        assert response.bio == "Test bio"


class TestResolveGroupResponse:
    """Tests for ResolveGroupResponse model."""

    def test_resolve_group_response_creation(self):
        """Test creating a ResolveGroupResponse instance."""
        response = ResolveGroupResponse(target_group_id=12345, display_name="Test User")
        assert response.target_group_id == 12345
        assert response.display_name == "Test User"


class TestGroupLinkResponse:
    """Tests for GroupLinkResponse model."""

    def test_group_link_response_with_link(self):
        """Test GroupLinkResponse with a link."""
        response = GroupLinkResponse(group_link="https://t.me/test")
        assert response.group_link == "https://t.me/test"

    def test_group_link_response_without_link(self):
        """Test GroupLinkResponse without a link (None)."""
        response = GroupLinkResponse()
        assert response.group_link is None


class TestCreateSessionResponse:
    """Tests for CreateSessionResponse model."""

    def test_create_session_response_creation(self):
        """Test creating a CreateSessionResponse instance."""
        response = CreateSessionResponse(user_group_link="https://t.me/session123")
        assert response.user_group_link == "https://t.me/session123"

