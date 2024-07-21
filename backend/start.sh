#!/bin/bash

# Run the Flask application
python app.py #&

# Run the second command
#sh -c "./llava-v1.5-7b-q4.llamafile --nobrowser"

# Wait for background processes to finish (if needed)
wait
