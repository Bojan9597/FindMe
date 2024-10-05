import sys
import os

# Add your application's directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app object
from app import app as application
