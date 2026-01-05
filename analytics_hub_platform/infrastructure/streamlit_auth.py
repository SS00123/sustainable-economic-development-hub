"""
Streamlit Authentication Module
Sustainable Economic Development Analytics Hub

Provides simple, secure authentication that works across:
- Local development (optional/bypass)
- Docker deployment (password auth)
- Streamlit Cloud (secrets-based)

Security Model:
1. Local Dev: AUTH_ENABLED=false bypasses authentication
2. Docker: Uses AUTH_PASSWORD environment variable
3. Streamlit Cloud: Uses st.secrets for credentials

This is the simplest secure approach that doesn't break local development.
"""

import hashlib
import hmac
import os
from functools import wraps
from typing import Callable

import streamlit as st


# =============================================================================
# CONFIGURATION
# =============================================================================

# Check if authentication is enabled (default: enabled in production)
def is_auth_enabled() -> bool:
    """Check if authentication is required."""
    env = os.getenv("ANALYTICS_HUB_ENV", "development")
    auth_enabled = os.getenv("AUTH_ENABLED", "auto").lower()
    
    if auth_enabled == "false":
        return False
    elif auth_enabled == "true":
        return True
    else:
        # Auto mode: enabled in production/staging, disabled in development
        return env in ("production", "staging")


def get_valid_credentials() -> dict[str, str]:
    """
    Get valid username/password combinations.
    
    Priority:
    1. Streamlit secrets (st.secrets.auth.users)
    2. Environment variables (AUTH_PASSWORD for default user)
    3. Default development credentials (only if AUTH_ENABLED=false)
    """
    credentials = {}
    
    # Try Streamlit secrets first
    try:
        if hasattr(st, "secrets") and "auth" in st.secrets:
            auth_config = st.secrets["auth"]
            if "users" in auth_config:
                for user in auth_config["users"]:
                    credentials[user["username"]] = user["password"]
            elif "password" in auth_config:
                credentials["admin"] = auth_config["password"]
    except Exception:
        pass
    
    # Try environment variable
    env_password = os.getenv("AUTH_PASSWORD")
    if env_password:
        credentials["admin"] = env_password
    
    # Default development credentials (ONLY if auth disabled)
    if not credentials and not is_auth_enabled():
        credentials["dev"] = "dev"
    
    return credentials


# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================


def hash_password(password: str) -> str:
    """Hash a password for secure storage/comparison."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a password against stored value.
    
    Supports both plain text (for secrets) and hashed passwords.
    """
    # First try direct comparison (for secrets)
    if hmac.compare_digest(stored_password, provided_password):
        return True
    
    # Try hash comparison
    if hmac.compare_digest(stored_password, hash_password(provided_password)):
        return True
    
    return False


def check_credentials(username: str, password: str) -> bool:
    """
    Validate username and password.
    
    Args:
        username: Provided username
        password: Provided password
    
    Returns:
        True if credentials are valid
    """
    valid_credentials = get_valid_credentials()
    
    if username not in valid_credentials:
        return False
    
    return verify_password(valid_credentials[username], password)


def login_form() -> bool:
    """
    Display a login form and handle authentication.
    
    Returns:
        True if user is authenticated
    """
    # Check if already authenticated
    if st.session_state.get("authenticated", False):
        return True
    
    # Check if auth is disabled
    if not is_auth_enabled():
        st.session_state.authenticated = True
        st.session_state.username = "dev"
        return True
    
    # Display login form
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: #1e293b;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Analytics Hub Login")
        st.markdown("Please enter your credentials to continue.")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    return False


def logout():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a page/function.
    
    Usage:
        @require_auth
        def render_protected_page():
            st.write("Secret content")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not login_form():
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def get_current_user() -> dict | None:
    """Get the currently authenticated user."""
    if not st.session_state.get("authenticated", False):
        return None
    
    return {
        "username": st.session_state.get("username", "unknown"),
        "is_admin": st.session_state.get("username") == "admin",
    }


# =============================================================================
# SIDEBAR AUTH WIDGET
# =============================================================================


def render_auth_sidebar():
    """Render authentication status in sidebar."""
    user = get_current_user()
    
    if user:
        with st.sidebar:
            st.divider()
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"👤 {user['username']}")
            with col2:
                if st.button("🚪", help="Logout"):
                    logout()
    elif is_auth_enabled():
        with st.sidebar:
            st.divider()
            st.caption("🔒 Not authenticated")


# =============================================================================
# DOCUMENTATION
# =============================================================================

"""
DEPLOYMENT CONFIGURATION
========================

1. LOCAL DEVELOPMENT
   - Set AUTH_ENABLED=false in environment or .env file
   - Or leave defaults (auto-disabled in development mode)
   
   Example .env:
   ```
   ANALYTICS_HUB_ENV=development
   AUTH_ENABLED=false
   ```

2. DOCKER DEPLOYMENT
   - Set AUTH_PASSWORD environment variable
   - Enable authentication
   
   Example docker-compose.yml:
   ```yaml
   environment:
     - ANALYTICS_HUB_ENV=production
     - AUTH_ENABLED=true
     - AUTH_PASSWORD=your_secure_password_here
   ```
   
   Or with docker run:
   ```bash
   docker run -e AUTH_ENABLED=true -e AUTH_PASSWORD=secret123 analytics-hub
   ```

3. STREAMLIT CLOUD
   - Add credentials to .streamlit/secrets.toml (in Streamlit Cloud dashboard)
   
   Example secrets.toml:
   ```toml
   [auth]
   password = "your_secure_password"
   
   # Or multiple users:
   [[auth.users]]
   username = "admin"
   password = "admin_password"
   
   [[auth.users]]
   username = "viewer"
   password = "viewer_password"
   ```

SECURITY NOTES
==============
- Never commit real passwords to version control
- Use strong, unique passwords in production
- Rotate passwords regularly
- Consider upgrading to SSO for enterprise deployment
"""
