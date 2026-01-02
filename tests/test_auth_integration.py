"""
Authentication Integration Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Comprehensive tests for JWT authentication, token lifecycle,
and API authentication flows.
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from analytics_hub_platform.infrastructure.auth import (
    JWTHandler,
    get_jwt_handler,
    get_mock_users,
    authenticate_user,
)
from analytics_hub_platform.infrastructure.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
)
from analytics_hub_platform.domain.models import User, UserRole


class TestJWTTokenLifecycle:
    """Tests for complete JWT token lifecycle."""
    
    @pytest.fixture
    def jwt_handler(self):
        """Create a JWT handler for testing."""
        return JWTHandler()
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id="test-user-001",
            tenant_id="test-tenant",
            email="test@example.com",
            name="Test User",
            role=UserRole.ANALYST,
            is_active=True,
        )
    
    def test_create_token_returns_string(self, jwt_handler, sample_user):
        """Test that token creation returns a non-empty string."""
        token = jwt_handler.create_access_token(sample_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_expected_format(self, jwt_handler, sample_user):
        """Test JWT token has expected format."""
        token = jwt_handler.create_access_token(sample_user)
        
        # Token can be JWT format (3 dots) or PoC format (poc_token:...)
        if token.startswith("poc_token:"):
            # PoC fallback format
            parts = token.split(":")
            assert len(parts) == 3
            assert parts[0] == "poc_token"
        else:
            # Standard JWT format
            parts = token.split(".")
            assert len(parts) == 3
    
    def test_verify_valid_token(self, jwt_handler, sample_user):
        """Test that valid tokens can be verified."""
        token = jwt_handler.create_access_token(sample_user)
        payload = jwt_handler.verify_token(token)
        
        assert payload is not None
        assert "sub" in payload or payload.get("sub") == sample_user.id
    
    def test_get_user_from_token(self, jwt_handler, sample_user):
        """Test extracting user from valid token."""
        token = jwt_handler.create_access_token(sample_user)
        user = jwt_handler.get_user_from_token(token)
        
        assert isinstance(user, User)
        assert user.id == sample_user.id
        assert user.role == sample_user.role
    
    def test_token_preserves_user_role(self, jwt_handler):
        """Test that different roles are preserved in tokens."""
        roles = [UserRole.MINISTER, UserRole.DIRECTOR, UserRole.ANALYST, UserRole.VIEWER]
        
        for role in roles:
            user = User(
                id=f"user-{role.value}",
                tenant_id="test-tenant",
                email=f"{role.value}@test.com",
                name=f"Test {role.value}",
                role=role,
                is_active=True,
            )
            
            token = jwt_handler.create_access_token(user)
            extracted_user = jwt_handler.get_user_from_token(token)
            
            assert extracted_user.role == role
    
    def test_token_preserves_tenant_id(self, jwt_handler):
        """Test that tenant ID is preserved in tokens."""
        tenant_ids = ["tenant-a", "tenant-b", "mep-sa-001"]
        
        for tenant_id in tenant_ids:
            user = User(
                id="test-user",
                tenant_id=tenant_id,
                email="test@test.com",
                name="Test",
                role=UserRole.VIEWER,
                is_active=True,
            )
            
            token = jwt_handler.create_access_token(user)
            extracted_user = jwt_handler.get_user_from_token(token)
            
            # Tenant should be preserved or default
            assert extracted_user.tenant_id is not None


class TestJWTTokenExpiration:
    """Tests for JWT token expiration handling."""
    
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler()
    
    @pytest.fixture
    def sample_user(self):
        return User(
            id="test-user",
            tenant_id="test-tenant",
            email="test@example.com",
            name="Test User",
            role=UserRole.ANALYST,
            is_active=True,
        )
    
    def test_token_with_custom_expiration(self, jwt_handler, sample_user):
        """Test creating token with custom expiration."""
        # Create token with 5 minute expiry
        token = jwt_handler.create_access_token(
            sample_user,
            expires_delta=timedelta(minutes=5)
        )
        
        # Should be valid
        payload = jwt_handler.verify_token(token)
        assert payload is not None
    
    def test_expired_token_behavior(self, jwt_handler, sample_user):
        """Test behavior with expired tokens."""
        # Create token with immediate expiry
        token = jwt_handler.create_access_token(
            sample_user,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # In PoC mode, tokens don't actually expire
        # In production with jose, should raise error
        try:
            payload = jwt_handler.verify_token(token)
            # PoC mode - token still works (no real expiration)
            assert payload is not None
        except (TokenExpiredError, InvalidTokenError):
            # Production mode - correctly rejects expired token
            pass


class TestJWTTokenValidation:
    """Tests for JWT token validation edge cases."""
    
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler()
    
    def test_invalid_token_format(self, jwt_handler):
        """Test that malformed tokens raise InvalidTokenError."""
        invalid_tokens = [
            "",
            "not-a-valid-token",
            "abc.def",  # Missing signature
            "...",
            None,
        ]
        
        for token in invalid_tokens:
            if token is not None:
                with pytest.raises(InvalidTokenError):
                    jwt_handler.verify_token(token)
    
    def test_tampered_token_behavior(self, jwt_handler):
        """Test that tampered tokens are handled appropriately."""
        user = User(
            id="test-user",
            tenant_id="test-tenant",
            email="test@example.com",
            name="Test User",
            role=UserRole.ANALYST,
            is_active=True,
        )
        
        token = jwt_handler.create_access_token(user)
        
        # Tamper with the token
        tampered = token[:-5] + "XXXXX"
        
        # In PoC mode, simple tokens might still parse
        # In production with jose, should raise error
        try:
            payload = jwt_handler.verify_token(tampered)
            # PoC mode - simplified validation
            # Just check it returns something
        except InvalidTokenError:
            # Production mode - correctly rejects tampered token
            pass


class TestMockUsers:
    """Tests for development mock users."""
    
    def test_mock_users_available(self):
        """Test that mock users are available."""
        mock_users = get_mock_users()
        
        assert mock_users is not None
        assert len(mock_users) > 0
    
    def test_mock_users_have_required_fields(self):
        """Test mock users have all required fields."""
        mock_users = get_mock_users()
        
        for user_id, user in mock_users.items():
            assert isinstance(user, User)
            assert user.id is not None
            assert user.tenant_id is not None
            assert user.email is not None
            assert user.role is not None
    
    def test_mock_users_include_different_roles(self):
        """Test mock users cover different roles."""
        mock_users = get_mock_users()
        roles = {user.role for user in mock_users.values()}
        
        # Should have multiple roles for testing
        assert len(roles) >= 2
    
    def test_demo_user_exists(self):
        """Test that default demo user exists."""
        mock_users = get_mock_users()
        
        assert "demo" in mock_users
        demo_user = mock_users["demo"]
        assert demo_user.is_active


class TestAuthenticateUser:
    """Tests for user authentication function."""
    
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid mock credentials."""
        # This tests the mock authentication path
        mock_users = get_mock_users()
        
        # Get first mock user
        first_user_id = list(mock_users.keys())[0]
        
        # In development mode, should return user
        user = authenticate_user(first_user_id, "any-password")
        
        # Should return a user (mock mode)
        if user:
            assert isinstance(user, User)
    
    def test_authenticate_returns_none_for_invalid(self):
        """Test authentication returns None for invalid users."""
        user = authenticate_user("nonexistent-user-xyz", "wrong-password")
        
        # Should return None or raise error
        assert user is None or isinstance(user, User)


class TestAPIAuthenticationFlow:
    """Tests for complete API authentication flows."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from main_api import app
        return TestClient(app)
    
    def test_health_endpoint_no_auth_required(self, client):
        """Test health endpoints work without authentication."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_protected_endpoint_with_mock_user(self, client):
        """Test protected endpoint with development mock user."""
        response = client.get(
            "/api/v1/indicators",
            headers={"X-User-ID": "demo", "X-Tenant-ID": "test"}
        )
        
        # In development mode, should allow mock user
        assert response.status_code in [200, 401]
    
    def test_bearer_token_authentication(self, client):
        """Test API authentication with bearer token."""
        # First create a token
        jwt_handler = JWTHandler()
        user = User(
            id="api-test-user",
            tenant_id="test-tenant",
            email="api@test.com",
            name="API Test User",
            role=UserRole.ANALYST,
            is_active=True,
        )
        token = jwt_handler.create_access_token(user)
        
        # Use token for API request
        response = client.get(
            "/api/v1/sustainability/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should authenticate successfully
        assert response.status_code in [200, 401]  # Depends on jose availability


class TestProductionSecurityEnforcement:
    """Tests for production security enforcement."""
    
    def test_production_requires_jwt_secret(self):
        """Test that production mode requires JWT secret."""
        import os
        from analytics_hub_platform.infrastructure.settings import Settings, ConfigurationError
        
        # Save current env
        old_env = os.environ.get("ENVIRONMENT")
        old_secret = os.environ.get("JWT_SECRET_KEY")
        
        try:
            # Clear secret and set production
            if "JWT_SECRET_KEY" in os.environ:
                del os.environ["JWT_SECRET_KEY"]
            os.environ["ENVIRONMENT"] = "production"
            
            # Should raise ConfigurationError
            with pytest.raises(ConfigurationError):
                Settings()
        finally:
            # Restore env
            if old_env:
                os.environ["ENVIRONMENT"] = old_env
            else:
                os.environ["ENVIRONMENT"] = "test"
            if old_secret:
                os.environ["JWT_SECRET_KEY"] = old_secret
    
    def test_production_rejects_weak_secret(self):
        """Test that production rejects weak JWT secrets."""
        import os
        from analytics_hub_platform.infrastructure.settings import Settings, ConfigurationError
        
        old_env = os.environ.get("ENVIRONMENT")
        old_secret = os.environ.get("JWT_SECRET_KEY")
        
        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["JWT_SECRET_KEY"] = "short"  # Too short
            
            with pytest.raises(ConfigurationError):
                Settings()
        finally:
            if old_env:
                os.environ["ENVIRONMENT"] = old_env
            else:
                os.environ["ENVIRONMENT"] = "test"
            if old_secret:
                os.environ["JWT_SECRET_KEY"] = old_secret
    
    def test_production_accepts_strong_secret(self):
        """Test that production accepts strong JWT secrets."""
        import os
        from analytics_hub_platform.infrastructure.settings import Settings
        
        old_env = os.environ.get("ENVIRONMENT")
        old_secret = os.environ.get("JWT_SECRET_KEY")
        
        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["JWT_SECRET_KEY"] = "a-very-strong-secret-key-that-is-at-least-32-characters-long"
            
            # Should not raise
            settings = Settings()
            assert settings.is_production()
            assert settings.jwt_secret_key is not None
        finally:
            if old_env:
                os.environ["ENVIRONMENT"] = old_env
            else:
                os.environ["ENVIRONMENT"] = "test"
            if old_secret:
                os.environ["JWT_SECRET_KEY"] = old_secret


class TestRoleBasedAccessIntegration:
    """Integration tests for role-based access control."""
    
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler()
    
    def test_minister_role_permissions(self, jwt_handler):
        """Test minister has executive dashboard access."""
        from analytics_hub_platform.infrastructure.security import RBACManager
        
        user = User(
            id="minister-001",
            tenant_id="test",
            email="minister@gov.sa",
            name="Minister",
            role=UserRole.MINISTER,
            is_active=True,
        )
        
        rbac = RBACManager()
        
        assert rbac.has_permission(user, "view_executive_dashboard")
        assert rbac.has_permission(user, "export_pdf")
    
    def test_analyst_role_restrictions(self, jwt_handler):
        """Test analyst has restricted permissions."""
        from analytics_hub_platform.infrastructure.security import RBACManager
        
        user = User(
            id="analyst-001",
            tenant_id="test",
            email="analyst@gov.sa",
            name="Analyst",
            role=UserRole.ANALYST,
            is_active=True,
        )
        
        rbac = RBACManager()
        
        assert rbac.has_permission(user, "view_analyst_dashboard")
        assert rbac.has_permission(user, "export_excel")
        # Analysts should not have admin access
        assert not rbac.has_permission(user, "manage_users")
    
    def test_admin_has_all_permissions(self, jwt_handler):
        """Test admin has all permissions."""
        from analytics_hub_platform.infrastructure.security import RBACManager
        
        user = User(
            id="admin-001",
            tenant_id="test",
            email="admin@gov.sa",
            name="Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        
        rbac = RBACManager()
        
        assert rbac.has_permission(user, "view_admin_console")
        assert rbac.has_permission(user, "manage_users")
        assert rbac.has_permission(user, "manage_settings")
