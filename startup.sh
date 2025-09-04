#!/bin/bash

# Azure startup script for the Flask application

# Upgrade pip first
pip install --upgrade pip

# Install numpy first to avoid compatibility issues
pip install numpy==1.24.4

# Install other dependencies
pip install -r requirements.txt

# Start the application with Gunicorn
gunicorn --bind 0.0.0.0:$PORT app:app
