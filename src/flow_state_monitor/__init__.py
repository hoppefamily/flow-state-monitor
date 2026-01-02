"""
flow-state-monitor: A tool to monitor market flow states.

This package provides functionality to detect flow states driven by forced
buying pressure from short covering. It analyzes borrow-rate dynamics (level,
delta, momentum) and price behavior to determine when pressure is active,
weakening, or gone.

This is NOT a trading signal or prediction tool. It monitors observable
flow states to support disciplined exit decisions.
"""

__version__ = "0.1.0"
__author__ = "flow-state-monitor contributors"
__license__ = "GPL-3.0"

from .config import Config
from .monitor import FlowStateMonitor

__all__ = ["FlowStateMonitor", "Config"]
