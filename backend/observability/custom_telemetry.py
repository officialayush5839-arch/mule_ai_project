import time
import psutil
import json
import logging
import sqlite3
from datetime import datetime
from collections import deque
from threading import Lock

class CustomTelemetryStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomTelemetryStore, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.lock = Lock()
        self.traces = deque(maxlen=2000)
        self.logs = deque(maxlen=2000)
        self.active_connections = 0
        self.api_requests = 0
        self.api_errors = 0
        self.predictions = 0
        self.start_time = time.time()
        
        # We will capture CPU/RAM snapshots every 5 seconds for chart history
        self.history = deque(maxlen=100)
        
    def add_trace(self, trace_data):
        with self.lock:
            self.traces.appendleft(trace_data)
            self.api_requests += 1
            if trace_data.get("status_code", 200) >= 400:
                self.api_errors += 1

    def add_log(self, log_data):
        with self.lock:
            self.logs.appendleft(log_data)
            
    def increment_prediction(self):
        with self.lock:
            self.predictions += 1

    def get_system_health(self):
        uptime = int(time.time() - self.start_time)
        return {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": uptime
        }
        
    def get_system_metrics(self):
        return {
            "total_requests": self.api_requests,
            "errors": self.api_errors,
            "predictions": self.predictions,
            "active_users": self.active_connections,
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent(),
            "uptime_seconds": int(time.time() - self.start_time)
        }

telemetry_store = CustomTelemetryStore()
