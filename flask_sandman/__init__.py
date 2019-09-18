"""*flask_sandman*'s main module."""
from flask_sandman.app import application as create_app
from flask_sandman.database import DATABASE as db
from flask_sandman.model import AutomapModel
