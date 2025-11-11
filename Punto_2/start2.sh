#!/bin/bash
source venv/bin/activate
uvicorn Punto_2.main:app --host 0.0.0.0 --port 8000
