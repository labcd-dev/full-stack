"""Pydantic schemas for admin monitoring metrics."""

from typing import List

from pydantic import BaseModel, Field


class MemoryMetrics(BaseModel):
    used_bytes: int
    total_bytes: int
    percent: float


class DiskMetrics(BaseModel):
    used_bytes: int
    total_bytes: int
    percent: float


class NetworkMetrics(BaseModel):
    bytes_sent: int
    bytes_recv: int
    sent_rate_bps: float
    recv_rate_bps: float


class ApiMetrics(BaseModel):
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    error_rate_percent: float
    requests_in_window: int


class MonitoringSnapshot(BaseModel):
    collected_at: str
    uptime_seconds: float
    cpu_percent: float
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    api: ApiMetrics


class MonitoringResponse(BaseModel):
    current: MonitoringSnapshot
    history: List[MonitoringSnapshot] = Field(default_factory=list)
