"""Admin blueprint package."""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import auth, routes  # noqa: F401, E402
