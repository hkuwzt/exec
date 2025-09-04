#!/bin/bash

# Azure startup script for the Flask application

# Install dependencies
pip install -r requirements.txt

# Start the application with Gunicorn
gunicorn --bind 0.0.0.0:$PORT app:app
