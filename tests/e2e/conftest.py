"""
Playwright E2E Tests Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Configuration and fixtures for end-to-end testing of the Streamlit application.
"""

import pytest
import subprocess
import time
import socket
from typing import Generator
from contextlib import contextmanager


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@contextmanager
def streamlit_server(port: int = 8502) -> Generator[str, None, None]:
    """
    Start a Streamlit server for testing.
    
    Args:
        port: Port to run the server on
        
    Yields:
        Server URL
    """
    # Check if port is available
    if is_port_in_use(port):
        # Assume server is already running
        yield f"http://localhost:{port}"
        return
    
    # Start Streamlit server
    process = subprocess.Popen(
        [
            "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", "localhost",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait for server to start
    max_wait = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_port_in_use(port):
            break
        time.sleep(0.5)
    else:
        process.kill()
        raise RuntimeError(f"Streamlit server did not start within {max_wait} seconds")
    
    try:
        yield f"http://localhost:{port}"
    finally:
        process.terminate()
        process.wait(timeout=5)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get the base URL for testing."""
    # Use the default Streamlit port
    return "http://localhost:8501"
