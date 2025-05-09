from flask import Blueprint

main_bp = Blueprint('main', __name__)

from financetracker.main import routes, forms, tracking_calculations, plotly_graphs