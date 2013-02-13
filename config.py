DATABASE = 'todo.db'
DEBUG = True
SECRET_KEY = 'development-key'

try:
    from local_config import *
except ImportError:
    pass
