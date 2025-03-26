from flask import Flask, request, render_template_string
import time
import threading
import multiprocessing
from prometheus_client import Counter, generate_latest, Gauge
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

CPU_LOAD = Counter('cpu_load_requests_total', 'Количество запросов для нагрузки CPU')
MEMORY_LOAD = Counter('memory_load_requests_total', 'Количество запросов для нагрузки памяти')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Потребляемая память в байтах')

memory_load = []

# HTML-страница с кнопками
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stress Test App</title>
</head>
<body>
    <h2>Stress Test App 🚀</h2>
    <button onclick="fetch('/cpu')">Нагрузить CPU</button>
    <button onclick="fetch('/memory')">Нагрузить Память (+500MB)</button>
    <button onclick="fetch('/memory/clear')">Очистить Память</button>
    <p>Открыть метрики: <a href="/metrics" target="_blank">/metrics</a></p>
    <p>Проверка состояния: <a href="/health" target="_blank">/health</a></p>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/health')
def health():
    return "OK"

@app.route('/cpu')
def load_cpu():
    CPU_LOAD.inc()
    logging.info('Нагрузка на CPU запущена')

    def cpu_task():
        start_time = time.time()
        while time.time() - start_time < 10:
            [x**2 for x in range(10000)]

    # Запускаем отдельный процесс для каждого ядра CPU
    processes = []
    num_cores = multiprocessing.cpu_count()
    for _ in range(num_cores):
        p = multiprocessing.Process(target=cpu_task)
        p.start()
        processes.append(p)

    return f"CPU load started on {num_cores} cores for ~10 seconds!"

@app.route('/memory')
def load_memory():
    MEMORY_LOAD.inc()
    logging.info('Нагрузка на память запущена')

    global memory_load
    memory_load.append(' ' * 500 * 1024 * 1024)
    MEMORY_USAGE.set(len(memory_load) * 500 * 1024 * 1024)

    return f"Memory loaded, current load: {len(memory_load) * 500} MB"

@app.route('/memory/clear')
def clear_memory():
    global memory_load
    memory_load = []
    MEMORY_USAGE.set(0)
    logging.info('Очистка нагрузки памяти')
    return "Memory cleared!"

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)