#!/usr/bin/env bash
# Install Python dependencies (if not already installed)
pip install --quiet -r requirements.txt
# Launch the FastAPI server with auto-reload
uvicorn main:app --reload

