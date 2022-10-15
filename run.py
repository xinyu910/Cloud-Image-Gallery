#!../venv/bin/python
"""from FrontEnd import webapp as front
from Memcache import webapp as mem
front.run('0.0.0.0', 5000, debug=False, use_reloader=False)
mem.run('0.0.0.0', 5001, debug=False, use_reloader=False)
"""

from werkzeug.serving import run_simple  # werkzeug development server
# use to combine each Flask app into a larger one that is dispatched based on prefix
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from Memcache import webapp as mem
from FrontEnd import webapp as front

applications = DispatcherMiddleware(front, {
    '/mem': mem
})

if __name__ == "__main__":
    """
    Two Flask instances are combine into a single object. Using "threaded = True", the function can call API within itself while dealing with user requests.
    """
    run_simple('0.0.0.0', 5000, applications,
               use_reloader=False,
               use_debugger=False,
               use_evalex=True,
               threaded=True)


