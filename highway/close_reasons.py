from enum import Enum

code = "code"
reason = "reason"

MALFORMED_HEADER = {code : 3001, reason : "Malformed header"}
ROUTE_DOES_NOT_EXIST = {code : 3002, reason : "Route does not exist"}
CONVERT_FAILED = {code : 1003, reason : "Convert failed"}
INTERNAL_ERROR = {code : 1011, reason : "Internal error"}
INVALID_STATE = {code : 3003, reason : "Invalid state"}