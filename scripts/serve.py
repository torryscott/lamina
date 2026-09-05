#!/usr/bin/env python3
"""Serve the repo locally for development.

    python3 scripts/serve.py [port]

Needed because the atlas and quiz fetch their data as JSON, and browsers
block fetch() on file:// URLs.
"""
import functools
import http.server
import os
import pathlib
import socketserver
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8731

os.chdir(ROOT)
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))


class Server(socketserver.TCPServer):
    allow_reuse_address = True


with Server(("127.0.0.1", PORT), Handler) as httpd:
    print(f"serving {ROOT} at http://localhost:{PORT}", flush=True)
    httpd.serve_forever()
