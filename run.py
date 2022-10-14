#!../venv/bin/python
from FrontEnd import webapp
from Memcache import webapp as mem

webapp.run('0.0.0.0', 5000, debug=False, use_reloader=False)
mem.run('0.0.0.0', 5001, debug=False, use_reloader=False)

