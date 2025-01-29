# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import multiprocessing
import os

bind = "0.0.0.0:5000"
workers = os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count())
worker_class = "uvicorn.workers.UvicornWorker"

# default directory for heartbeat file is in /tmp, which in some Linux distros
# is stored in memory via tmpfs filesystem. Docker containers, however, do not
# have /tmp on tmpfs by default - so we use /dev/shm
# https://pythonspeed.com/articles/gunicorn-in-docker/
worker_tmp_dir = "/dev/shm"

timeout = 600
keepalive = 100

accesslog = "-"
errorlog = "-"
capture_output = True
