from ujson import dumps as json_dumps

PREPARE_COLLECTION = lambda data: json_dumps(data).encode()

NoneType = None.__class__

PREPARERS = {
	str : lambda data: data.encode(),
	int : lambda data: str(data).encode(),
	float : lambda data: str(data).encode(),
	# Faster than int(data)
	bool : lambda data: str(1 if data else 0).encode(),
	list : PREPARE_COLLECTION,
	dict : PREPARE_COLLECTION,
	tuple : PREPARE_COLLECTION,
	bytes : lambda data: data,
	NoneType : lambda data: "".encode()
}


class PrepareFailedError(ValueError):
	def __init__(self):
		super(ValueError, self).__init__("preparation failed (data type unsupported)")



def prepare(original_data, encoder=None):
	original_data_type = type(original_data)

	try:
		return PREPARERS[original_data_type](original_data), \
		original_data_type

	except KeyError:
		raise PrepareFailedError()
	except ValueError:
		raise PrepareFailedError()
	except TypeError:
		raise PrepareFailedError()