"""
Vercel Serverless Entry Point
Exposes the FastAPI ASGI app for Vercel deployment.
"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.server import app
