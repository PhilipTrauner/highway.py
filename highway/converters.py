from ujson import loads as json_loads

NoneType = None.__class__
CONVERT_COLLECTION = lambda data: json_loads(data.decode())

CONVERTERS = {
	str : lambda data: data.decode(),
	int : lambda data: int(data.decode()),
	float : lambda data: float(data.decode()),
	bool : lambda data: bool(int(data.decode())),
	list : CONVERT_COLLECTION,
	dict : CONVERT_COLLECTION,
	tuple : CONVERT_COLLECTION,
	bytes : lambda data: data,
	NoneType : lambda data: None
}


class ConvertFailedError(ValueError):
	def __init__(self, original_error):
		super(ValueError, self).__init__("conversion failed")


class UnknownDataTypeError(ConvertFailedError):
	def __init__(self, type_):
		super(ConvertFailedError, self).__init__("data type unknown: '%s'" % type_)


def convert(binary_data, data_type):
	try:
		return CONVERTERS[data_type](binary_data)
	except KeyError:
		raise UnknownDataTypeError(data_type)
	except ValueError:
		raise ConvertFailedError()