#!/usr/bin/env python3
"""
Simple Update Server for Project Zozfil
Serves the updates folder over HTTP for testing updates.
"""

import http.server
import socketserver
import os

# Configuration
PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(__file__), "updates")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Ensure updates directory exists
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

print(f"Serving updates from {DIRECTORY} on port {PORT}")
print(f"Access at: http://localhost:{PORT}")
print("Press Ctrl+C to stop")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()