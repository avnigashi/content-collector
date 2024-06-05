#!/bin/bash

# Install the requirements from requirements.txt
pip install -r requirements.txt

# Check if the installation was successful
if [ $? -eq 0 ]; then
    # Execute main.py
    python main.py
else
    echo "Failed to install requirements."
    exit 1
fi
