import argparse
import logging

from flask import Flask
from gevent.pywsgi import WSGIServer
from library.logger import setup_logging

from api.movie.lk21 import lk21

setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    argp = argparse.ArgumentParser(description="API")
    argp.add_argument(
        "-p", "--port", dest="port", help="engine port listened", type=int, default=8002
    )
    argp.add_argument("-apps", "--apps", dest="apps", help="apps listened")

    args = argp.parse_args()

    from api import sdk

    class App(Flask):
        def __init__(self, import_name, **kwargs):
            super().__init__(import_name)

    app = App(__name__)
    app.register_blueprint(sdk)
    application = app

    logger.info(f"listening to http://10.0.2.15:{args.port}")
    http_server = WSGIServer(
        ("10.0.2.15", args.port),
        application, log=logger
    )
    http_server.serve_forever()
