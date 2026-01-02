"""
Rate Limiting Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for sliding window rate limiter with token bucket.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from analytics_hub_platform.infrastructure.exceptions import RateLimitError
from analytics_hub_platform.infrastructure.rate_limiting import (
    RateLimitConfig,
    RateLimiterManager,
    SlidingWindowRateLimiter,
    get_rate_limiter_manager,
    rate_limited,
)


class TestSlidingWindowRateLimiter:
    """Tests for sliding window rate limiter."""

    @pytest.fixture
    def limiter(self):
        """Create a test rate limiter."""
        config = RateLimitConfig(
            max_requests=5,
            window_seconds=10,
            burst_size=5,  # Match max_requests to avoid burst limiting
            key_prefix="test",
        )
        return SlidingWindowRateLimiter(config)

    def test_allows_requests_within_limit(self, limiter):
        """Test that requests within limit are allowed."""
        for i in range(5):
            allowed, remaining, _ = limiter.acquire("user1")
            assert allowed, f"Request {i + 1} should be allowed"
            assert remaining == 4 - i

    def test_blocks_requests_over_limit(self, limiter):
        """Test that requests over limit are blocked."""
        # Use up all slots
        for _ in range(5):
            limiter.acquire("user1")

        # Next request should be blocked
        allowed, remaining, retry_after = limiter.acquire("user1")
        assert not allowed
        assert remaining == 0
        assert retry_after > 0

    def test_check_does_not_consume_quota(self, limiter):
        """Test that check() doesn't consume quota."""
        # Check multiple times
        for _ in range(10):
            allowed, remaining, _ = limiter.check("user1")
            assert allowed
            assert remaining == 5

        # Quota should still be full
        allowed, remaining, _ = limiter.check("user1")
        assert allowed
        assert remaining == 5

    def test_different_users_have_separate_limits(self, limiter):
        """Test per-user isolation."""
        # Use up user1's quota
        for _ in range(5):
            limiter.acquire("user1")

        # user2 should still have full quota
        allowed, remaining, _ = limiter.check("user2")
        assert allowed
        assert remaining == 5

    def test_acquire_or_raise_success(self, limiter):
        """Test acquire_or_raise returns remaining count."""
        remaining = limiter.acquire_or_raise("user1")
        assert remaining == 4

    def test_acquire_or_raise_exception(self, limiter):
        """Test acquire_or_raise raises RateLimitError."""
        # Use up quota
        for _ in range(5):
            limiter.acquire("user1")

        with pytest.raises(RateLimitError) as exc_info:
            limiter.acquire_or_raise("user1")

        error = exc_info.value
        assert error.details["limit"] == 5
        assert error.details["retry_after"] > 0

    def test_reset_clears_state(self, limiter):
        """Test that reset clears rate limit state."""
        # Use some quota
        for _ in range(3):
            limiter.acquire("user1")

        allowed, remaining, _ = limiter.check("user1")
        assert remaining == 2

        # Reset
        limiter.reset("user1")

        # Should have full quota again
        allowed, remaining, _ = limiter.check("user1")
        assert remaining == 5

    def test_get_stats(self, limiter):
        """Test statistics retrieval."""
        # Initial stats
        stats = limiter.get_stats("user1")
        assert stats["current_count"] == 0
        assert stats["remaining"] == 5

        # After some requests
        limiter.acquire("user1")
        limiter.acquire("user1")

        stats = limiter.get_stats("user1")
        assert stats["current_count"] == 2
        assert stats["remaining"] == 3

    def test_key_prefix_applied(self, limiter):
        """Test that key prefix is applied."""
        limiter.acquire("user1")

        # Internal key should have prefix
        internal_key = limiter._get_key("user1")
        assert internal_key == "test:user1"


class TestRateLimiterThreadSafety:
    """Tests for thread safety of rate limiter."""

    def test_concurrent_acquire(self):
        """Test concurrent acquire operations."""
        config = RateLimitConfig(
            max_requests=100,
            window_seconds=60,
            burst_size=100,
        )
        limiter = SlidingWindowRateLimiter(config)

        success_count = 0
        failure_count = 0
        lock = threading.Lock()

        def acquire_slot():
            nonlocal success_count, failure_count
            allowed, _, _ = limiter.acquire("concurrent-test")
            with lock:
                if allowed:
                    success_count += 1
                else:
                    failure_count += 1

        # Run 150 concurrent requests (100 should succeed)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(acquire_slot) for _ in range(150)]
            for future in as_completed(futures):
                future.result()

        assert success_count == 100
        assert failure_count == 50

    def test_no_race_conditions(self):
        """Test that no race conditions occur."""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=60,
        )
        limiter = SlidingWindowRateLimiter(config)

        results = []

        def rapid_acquire():
            for _ in range(5):
                allowed, remaining, _ = limiter.acquire("race-test")
                results.append((allowed, remaining))

        threads = [threading.Thread(target=rapid_acquire) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Total successful acquires should be exactly 10
        successful = sum(1 for allowed, _ in results if allowed)
        assert successful == 10


class TestRateLimiterManager:
    """Tests for rate limiter manager."""

    def test_singleton_pattern(self):
        """Test that manager is a singleton."""
        manager1 = get_rate_limiter_manager()
        manager2 = get_rate_limiter_manager()
        assert manager1 is manager2

    def test_default_limiters_exist(self):
        """Test that default limiters are created."""
        manager = RateLimiterManager()

        # Should have api, export, and auth limiters
        assert manager.get("api") is not None
        assert manager.get("export") is not None
        assert manager.get("auth") is not None

    def test_register_custom_limiter(self):
        """Test registering custom rate limiter."""
        manager = RateLimiterManager()

        config = RateLimitConfig(
            max_requests=50,
            window_seconds=30,
            key_prefix="custom",
        )

        limiter = manager.register("custom", config)
        assert limiter is not None
        assert manager.get("custom") is limiter

    def test_get_unknown_limiter_raises(self):
        """Test that getting unknown limiter raises KeyError."""
        manager = RateLimiterManager()

        with pytest.raises(KeyError):
            manager.get("nonexistent")

    def test_convenience_methods(self):
        """Test convenience methods for common limiters."""
        manager = RateLimiterManager()

        # These should work without raising
        allowed, remaining, _ = manager.check_api("test-user")
        assert allowed

        allowed, remaining, _ = manager.check_export("test-user")
        assert allowed

        allowed, remaining, _ = manager.check_auth("test-user")
        assert allowed


class TestRateLimitedDecorator:
    """Tests for @rate_limited decorator."""

    def test_decorated_function_works(self):
        """Test that decorated function executes normally."""
        call_count = 0

        @rate_limited("api", key_func=lambda x: x)
        def my_function(user_id):
            nonlocal call_count
            call_count += 1
            return f"result for {user_id}"

        result = my_function("user1")
        assert result == "result for user1"
        assert call_count == 1

    def test_decorator_respects_limit(self):
        """Test that decorator enforces rate limits."""
        # Create a strict limiter for testing
        manager = get_rate_limiter_manager()
        config = RateLimitConfig(
            max_requests=3,
            window_seconds=60,
            key_prefix="decorator-test",
        )
        manager.register("decorator_test", config)

        call_count = 0

        @rate_limited("decorator_test", key_func=lambda x: x)
        def limited_function(user_id):
            nonlocal call_count
            call_count += 1
            return "ok"

        # First 3 calls should succeed
        for _ in range(3):
            limited_function("test-user")

        assert call_count == 3

        # 4th call should raise
        with pytest.raises(RateLimitError):
            limited_function("test-user")

        assert call_count == 3  # Shouldn't have incremented

    def test_decorator_key_func(self):
        """Test that key_func extracts correct identifier."""
        manager = get_rate_limiter_manager()
        config = RateLimitConfig(
            max_requests=2,
            window_seconds=60,
            key_prefix="keyfunc-test",
        )
        manager.register("keyfunc_test", config)

        @rate_limited("keyfunc_test", key_func=lambda uid, **kw: uid)
        def function_with_args(user_id, data=None):
            return user_id

        # User1 gets 2 calls
        function_with_args("user1", data="a")
        function_with_args("user1", data="b")

        # User1's 3rd call should fail
        with pytest.raises(RateLimitError):
            function_with_args("user1", data="c")

        # User2 should still work
        result = function_with_args("user2", data="x")
        assert result == "user2"


class TestRateLimitWindow:
    """Tests for sliding window behavior."""

    def test_window_slides_correctly(self):
        """Test that old requests expire from window."""
        config = RateLimitConfig(
            max_requests=3,
            window_seconds=1,  # 1 second window for fast testing
        )
        limiter = SlidingWindowRateLimiter(config)

        # Use up quota
        for _ in range(3):
            limiter.acquire("user1")

        # Should be blocked
        allowed, _, _ = limiter.check("user1")
        assert not allowed

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        allowed, remaining, _ = limiter.check("user1")
        assert allowed
        assert remaining == 3


class TestBurstHandling:
    """Tests for token bucket burst handling."""

    def test_burst_limit_enforced(self):
        """Test that burst limit prevents rapid requests."""
        config = RateLimitConfig(
            max_requests=100,  # High limit
            window_seconds=60,
            burst_size=3,  # But low burst
        )
        limiter = SlidingWindowRateLimiter(config)

        # Rapid requests should hit burst limit
        success = 0
        for _ in range(10):
            allowed, _, _ = limiter.acquire("burst-test")
            if allowed:
                success += 1

        # Should be limited by burst size (initially 3 tokens)
        # Plus tokens that refill during execution
        assert success <= 5  # Some tolerance for refill
