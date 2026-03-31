#!/bin/bash

# Name of the virtual environment directory
ENV_DIR="venv"

# Function to create and activate the virtual environment
install_dependencies() {    
source $ENV_DIR/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    echo "Dependencies installed"
}

# Check if the virtual environment directory exists
if [ -d "$ENV_DIR" ]; then
    echo "Environment exists."
    install_dependencies
else
    echo "Environment does not exist. Setting up..."
    python3 -m venv $ENV_DIR
    install_dependencies
fi