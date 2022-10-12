#!../venv/bin/python
from FrontEnd import webapp as front
from Memcache import webapp as mem
front.run('0.0.0.0', 5000, debug=False)
mem.run('0.0.0.0', 5001, debug=False)

