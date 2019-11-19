def typecast(val,thetype,default):
	"""
	Validation function which checks if the variable `var` can be typecast to datatype `thetype`.
	If there was any exception encountered, return the default value specified
	"""
	try:
		if (thetype == bool) and not isinstance(val, thetype):
			return default
		return thetype(val)
	except:
		return default
	
def check_valid_cash(cash):
	"""
	Function checks cash passed in through actions by the agent.
	If cash can't be typecast to int, the cash amount is considered 
	invalid and invalid flows for defaulting would take place.
	"""
	try:
		cash = int(cash)
	except:
		return 0
	if cash < 0:
		return 0
	return cash

def replace_last(source_string, replace_what, replace_with):
    head, _sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail

#Generator for circular range
def crange(start, end, modulo):
    if start > end:
        while start < modulo:
            yield start
            start += 1
        start = 0   
    while start <= end:
        yield start
        start += 1