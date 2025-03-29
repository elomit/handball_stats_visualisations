# TODO image sizing+placing
# TODO Titles
class Analysis(object):
	def __init__(self, image_path: str = None):
		self.image_path = image_path
		self.sub_analyses: list['Analysis'] = []

	def add_analysis(self, analyse: 'Analysis'):
		self.sub_analyses.append(analyse)
