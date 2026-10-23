#!/bin/bash
source /opt/virt/bin/activate
exec uvicorn app.main:app --host=0.0.0.0 --port=5005 --root-path=/espada
