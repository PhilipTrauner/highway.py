from __future__ import print_function
from time import strftime
from inspect import getmodule, stack, currentframe, getframeinfo
from sys import stderr
from sys import stdout

# Formatting
BOLD = "\033[1m"
HIDDEN = "\033[2m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
INVERTED = "\033[7m"
HIDDEN = "\033[8m"

# Backgrounds
BACKGROUND_DEFAULT = "\033[49m"
BACKGROUND_BLACK = "\033[40m"
BACKGROUND_RED = "\033[41m"
BACKGROUND_GREEN = "\033[42m"
BACKGROUND_YELLOW = "\033[43m"
BACKGROUND_BLUE = "\033[44m"
BACKGROUND_MAGENTA = "\033[45m"
BACKGROUND_CYAN = "\033[46m"
BACKGROUND_LIGHT_GRAY = "\033[47m"
BACKGROUND_DARK_GRAY = "\033[100m"
BACKGROUND_LIGHT_RED = "\033[101m"
BACKGROUND_LIGHT_GREEN = "\033[102m"
BACKGROUND_LIGHT_YELLOW = "\033[103m"
BACKGROUND_LIGHT_BLUE = "\033[104m"
BACKGROUND_LIGHT_MAGENTA = "\033[105m"
BACKGROUND_LIGHT_CYAN = "\033[106m"
BACKGROUND_WHITE = "\033[107m"

# Colors
DEFAULT = "\033[39m" 
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHT_GREY = "\033[37m"
DARK_GRAY = "\033[90m"
LIGHT_RED = "\033[91m"
LIGHT_GREEN = "\033[92m"
LIGHT_YELLOW = "\033[93m"
LIGHT_BLUE = "\033[94m"
LIGHT_MAGENTA = "\033[95m"
LIGHT_CYAN = "\033[96m"

CACHED_MODULES = {}

# If the stack becomes too complex to figure out a caller we go through and assume the first valid module is the caller.
# This works reasonably well but isn't 100% accurate and will only happen if the caller is a thread.
def print_out(message, color, file):
	stack_ = stack()
	# Interestingly the if statement below is not executed when excepting KeyboardInterrupts. Weird.
	# To prevent a crash we assume the module's name is 'Unknown'
	module = "Unknown"
	if getmodule(stack_[2][0]) == None:
		for i in stack_[2:]:
			if getmodule(i[0]) != None:
				try:
					module = CACHED_MODULES[i[0].f_code]
				except KeyError:
					module = getmodule(i[0]).__name__
					CACHED_MODULES[i[0].f_code] = module
	else:
		try:
			module = CACHED_MODULES[stack_[2][0].f_code]
		except KeyError:
			module = getmodule(stack_[2][0]).__name__
			CACHED_MODULES[stack_[2][0].f_code] = module
	print("\033[32m%s\033[0m:%i → %s%s\033[0m" % (
		module, stack_[2][0].f_lineno, color, 
		message), file=file)
	file.flush()


def info(message, color=""):
	print_out(message, color, stdout)


def header(message):
	print_out(message, MAGENTA, stdout)


def warning(message):
	print_out(message, YELLOW, stderr)


def error(message):
	print_out(message, RED, stderr)


def success(message):
	print_out(message, GREEN, stdout)


if __name__ == "__main__":
	info("Hi!", color=UNDERLINE+BACKGROUND_GREEN+RED)
	header("This is a header")
	warning("This is a warning")    # > stderr
	error("This is an error")       # > stderr
	success("Great success!")