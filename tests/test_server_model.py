# tests/test_server_model.py
import time
import pytest
from server_model import ServerModel, RequestEvent

def test_enqueue_and_step_basic():
    s = ServerModel(processing_capacity_per_sec=10.0)
    now = time.time()
    # 3 requêtes coût 2 => total 6 < capacité (10)
    s.enqueue(RequestEvent(now, cost=2.0))
    s.enqueue(RequestEvent(now, cost=2.0))
    s.enqueue(RequestEvent(now, cost=2.0))
    stats = s.step(dt=1.0)
    assert stats['processed'] == 3
    assert stats['queue_len'] == 0
    assert abs(stats['processed_cost'] - 6.0) < 1e-6

def test_queue_remains_if_over_capacity():
    s = ServerModel(processing_capacity_per_sec=5.0)
    now = time.time()
    s.enqueue(RequestEvent(now, cost=3.0))
    s.enqueue(RequestEvent(now, cost=3.0))
    stats = s.step(dt=1.0)
    # capacité=5 -> peut traiter une requête (3) et laisser la 2e
    assert stats['processed'] == 1
    assert stats['queue_len'] == 1

def test_get_state_thresholds():
    s = ServerModel(processing_capacity_per_sec=1.0, warning_threshold=50, overload_threshold=80)
    now = time.time()
    s.enqueue(RequestEvent(now, cost=10.0))
    s.step(dt=1.0)
    state, load = s.get_state()
    assert state in ("CHARGÉ", "SURCHARGÉ")
