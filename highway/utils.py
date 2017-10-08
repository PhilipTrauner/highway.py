from traceback import print_exception
from sys import exc_info

def capture_trace():
	exc_type, exc_value, exc_traceback = exc_info()
	print_exception(exc_type, exc_value, exc_traceback)

def reverse_dict(dict_):
	return {v : k for k, v in dict_.items()}