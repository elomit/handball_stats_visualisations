# TODO Titles
class Analysis(object):
	def __init__(self, image_path: str = None, width: float = 8, height: float = 5, top: float = 1, left: float = 1):
		self.left = left
		self.top = top
		self.height = height
		self.width = width
		self.image_path = image_path
		self.sub_analyses: list['Analysis'] = []

	def add_analysis(self, analyse: 'Analysis'):
		self.sub_analyses.append(analyse)
