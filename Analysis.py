import re


def safe_file_name(name: str) -> str:
	"""Name (e.g. of a player) usable in a file name: no surrounding spaces, characters like / replaced by _."""

	return re.sub(r'[^\w\-(). ,]', '_', name.strip())


class Analysis(object):
	def __init__(self, image_path: str = None, width: float = 8, height: float = 5, top: float = 1, left: float = 1,
				 title: str = None):
		# analyses with a title get an entry in the index of the pdf, sub analyses are indented below it
		self.title = title
		self.left = left
		self.top = top
		self.height = height
		self.width = width
		self.image_path = image_path
		self.sub_analyses: list['Analysis'] = []

	def add_analysis(self, analyse: 'Analysis'):
		self.sub_analyses.append(analyse)
