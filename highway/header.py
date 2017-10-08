from struct import pack as struct_pack
from struct import unpack as struct_unpack
from struct import error as struct_error
from struct import calcsize as struct_calcsize

from .preparers import prepare

from .data_types import DATA_TYPES, REVERSE_DATA_TYPES

PACK_FORMAT = "BH"
METADATA_LENGTH = struct_calcsize(PACK_FORMAT)


class HeaderLayoutInvalidError(ValueError):
	def __init__(self, original_error):
		self.original_error = original_error
		super(ValueError, self).__init__("header layout invalid")


def create_metadata(data_type, converted_route):
	return struct_pack(PACK_FORMAT, DATA_TYPES[data_type], converted_route)


def pack_message(data, exchange_route):
	data, original_data_type = prepare(data)
	return create_metadata(original_data_type, exchange_route) + data


def parse_metadata(message):
	try:
		metadata = struct_unpack(PACK_FORMAT, message[:METADATA_LENGTH])
		return REVERSE_DATA_TYPES[metadata[0]], metadata[1]
	except struct_error as e:
		raise HeaderLayoutInvalidError(e)