class ResolutionRule(object):
	"""docstring for PropertyResolutionRule"""
		
	@staticmethod
	def get_rule(where_clause, min_resolution=None, max_resolution=None):
		min_pred = (lambda res : res >= min_resolution) if min_resolution else (lambda res: True)
		max_pred = (lambda res : res < max_resolution) if max_resolution else (lambda res: True)
		# Return function that returns where_clause if rule matched, else None
		return lambda res : where_clause if min_pred(res) and max_pred(res) else None

		