#!/bin/bash
set -e

uvicorn app.main:app --host 0.0.0.0 --port 5001 --root-path /evanoso
