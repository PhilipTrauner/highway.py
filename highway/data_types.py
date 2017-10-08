from .utils import reverse_dict

NoneType = None.__class__

DATA_TYPES = {
	str : 0, 
	int : 1,
	float : 2, 
	bool : 3,
	list : 4, 
	dict : 5,
	tuple : 6,
	bytes : 7,
	NoneType : 8 
}


REVERSE_DATA_TYPES = reverse_dict(DATA_TYPES)