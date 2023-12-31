from flask import Blueprint
from flask_restx import Api

sdk = Blueprint("sdk", __name__)
api = Api(
    app=sdk,
    version="4.0",
    title="Crawler",
    description="API Downloader & Searcher",
)
