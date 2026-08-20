#!/bin/bash

uvicorn app.main:app --host 0.0.0.0 --port 5000 --root-path /marquiso
