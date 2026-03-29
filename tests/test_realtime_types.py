# -*- coding: utf-8 -*-
"""Concurrency regression tests for realtime circuit-breaker state."""

import threading
import time
import unittest

from data_provider.realtime_types import CircuitBreaker


class CircuitBreakerConcurrencyTestCase(unittest.TestCase):
    def test_half_open_allows_only_one_concurrent_probe(self):
        breaker = CircuitBreaker(
            failure_threshold=1,
            cooldown_seconds=0.01,
            half_open_max_calls=1,
        )
        breaker.record_failure("akshare_em", "boom")
        time.sleep(0.02)

        barrier = threading.Barrier(2)
        allowed = []
        errors = []

        def worker():
            try:
                barrier.wait(timeout=1)
                allowed.append(breaker.is_available("akshare_em"))
            except Exception as exc:  # pragma: no cover - thread collection
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)

        self.assertEqual(errors, [])
        self.assertCountEqual(allowed, [True, False])
        self.assertEqual(breaker.get_status()["akshare_em"], CircuitBreaker.HALF_OPEN)

    def test_concurrent_record_updates_keep_state_consistent(self):
        breaker = CircuitBreaker(
            failure_threshold=3,
            cooldown_seconds=60.0,
            half_open_max_calls=1,
        )
        barrier = threading.Barrier(4)
        errors = []

        def record_success():
            try:
                barrier.wait(timeout=1)
                for _ in range(100):
                    breaker.record_success("tushare")
            except Exception as exc:  # pragma: no cover - thread collection
                errors.append(exc)

        def record_failure():
            try:
                barrier.wait(timeout=1)
                for _ in range(100):
                    breaker.record_failure("tushare", "network")
            except Exception as exc:  # pragma: no cover - thread collection
                errors.append(exc)

        threads = [
            threading.Thread(target=record_success),
            threading.Thread(target=record_success),
            threading.Thread(target=record_failure),
            threading.Thread(target=record_failure),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)

        self.assertEqual(errors, [])
        state = breaker._states["tushare"]
        self.assertIn(state["state"], {CircuitBreaker.CLOSED, CircuitBreaker.OPEN, CircuitBreaker.HALF_OPEN})
        self.assertGreaterEqual(state["failures"], 0)
        self.assertGreaterEqual(state["half_open_calls"], 0)


if __name__ == "__main__":
    unittest.main()
