#!/bin/bash
exec gunicorn --config gunicorn_config.py wsgi:app

# docker run --name jwt_server --network work_repo-network -v /home/nguacon01/work/jwt_server:/jwt_server --restart always nguacon01/jwt_server:latest