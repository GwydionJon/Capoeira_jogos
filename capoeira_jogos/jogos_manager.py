from waitress import serve
import time
import webbrowser  # For launching web pages
from threading import Timer  # For waiting before launching web page

from dash_app import server


def open_browser():
    """
    Open browser to localhost
    """

    webbrowser.open_new("http://127.0.0.1:8080/")


Timer(1, open_browser).start()
serve(server)
