#!../venv/bin/python

from werkzeug.serving import run_simple  # werkzeug development server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
"""IMPORT FLASK INSTANCES FROM FOLDER Memcache AND FrontEnd"""
from Memcache import webapp as mem
from FrontEnd import webapp as front

"""MERGE TWO FLASK INSTANCES: MEMCACHE AND FRONTEDND"""
applications = DispatcherMiddleware(front, {
    '/mem': mem
})

if __name__ == "__main__":
    """THREADED = TRUE FOR TWO INSTANCE WORKING TOGETHER"""
    run_simple('0.0.0.0', 5000, applications,
               use_reloader=False,
               use_debugger=False,
               use_evalex=True,
               threaded=True)


