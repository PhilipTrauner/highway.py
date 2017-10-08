from .utils import reverse_dict
from . import log as logging

META_ROUTE = "meta"
META_ROUTE_INDEX = 0

BASE_PEER_EXCHANGE_ROUTES = {META_ROUTE_INDEX : META_ROUTE}
BASE_PEER_REVERSE_EXCHANGE_ROUTES = {META_ROUTE : META_ROUTE_INDEX}


def create_exchange_routes(routes):
	exchange_map = {META_ROUTE_INDEX : META_ROUTE}
	exchange_id = 1
	for route in routes:
		if route != META_ROUTE:
			exchange_map[exchange_id] = route
			exchange_id += 1
	return exchange_map


def convert_exchange_routes(routes):
	exchange_routes = {}
	for key in routes:
		if key.isnumeric() and type(routes[key]) is str:
			exchange_routes[int(key)] = routes[key]
		else:
			return None
	return exchange_routes


def assemble_routing(routes):
	reverse_routes = reverse_dict(routes)
	exchange_routes = create_exchange_routes(routes)
	reverse_exchange_routes = reverse_dict(exchange_routes)
	return reverse_routes, exchange_routes, reverse_exchange_routes


async def meta_route(data, handler):
	route_exchange_successful = False
	peer_exchange_routes = None

	if type(data) is dict:
		peer_exchange_routes = convert_exchange_routes(data)
		if peer_exchange_routes != None:
			route_exchange_successful = True

	if route_exchange_successful:
		handler._base.peer_exchange_routes = peer_exchange_routes
		if handler.debug:
			logging.success("Received peer exchange routes: %s" % str(data))
		handler._base.peer_reverse_exchange_routes = \
			reverse_dict(handler._base.peer_exchange_routes)
		
		if hasattr(handler._base, "on_exchange"):	
			await handler._base.on_exchange(handler)
			
		if hasattr(handler, "on_ready"):
			await handler.on_ready()	
	else:
		logging.error("Received invalid exchange routes.")
		handler.close(reason="Invalid exchange routes")