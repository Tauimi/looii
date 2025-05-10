import multiprocessing
import os

# Базовые настройки
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 60
keepalive = 5
errorlog = "-"
loglevel = "info"
accesslog = "-"
preload_app = True

# Настройки для бесплатного плана
max_requests = 1000
max_requests_jitter = 50
worker_connections = 1000 