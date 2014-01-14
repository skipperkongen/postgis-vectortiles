from util import BoundingBox 
from math import ceil

def gridset_by_srid(srid):
	if srid == '3857':
		return Grid3857()
	else:
		raise ValueError("Unsupported srid: %s" % srid)

class Grid(object):
	"""docstring for Grid"""
	def __init__(self, unit=None, bounds=None):
		super(Grid, self).__init__()
		self.bounds = bounds
		self.width = bounds.maxx - bounds.minx
		self.height = bounds.maxy - bounds.miny
	
	def get_bbox(self, x, y, z, tile_pixel_dims=(256,256)):
		
		self.validate(x,y,z)
				
		bbox_width, bbox_height = self.get_cell_size( z )

		# X's
		minx = self.bounds.minx + (x * bbox_width)
		maxx = self.bounds.minx + (x * bbox_width) + bbox_width
		# Y's
		maxy = self.bounds.maxy - (y * bbox_height)
		miny = self.bounds.maxy - (y * bbox_height) - bbox_height
		
		resolution = float(bbox_width) / tile_pixel_dims[0]
		
		return BoundingBox(minx=minx, miny=miny, maxx=maxx, maxy=maxy), resolution
	
	def get_cell_size(self, z):
		cell_width = self.width
		cell_height = self.height		
		for i in range(z):
			cell_width /= 2.0
			cell_height /= 2.0
		return (cell_width, cell_height)		
	
	def get_resolution(self, z, image_dimensions=(256.0,256.0)):
		cell_width, cell_height = self.get_cell_size( z )
		return cell_width / image_dimensions[0], cell_height / image_dimensions[1]
		
	def validate(self, x, y, z):
		raise NotImplementedError("Not implemented")

class Grid3857(Grid):
	"""docstring for Grid3857"""
	def __init__(self):
		# echo 180 85 | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:3857
		#super(Grid3857, self).__init__(unit="m", bounds=BoundingBox(minx=-20037508.342789244,miny=-19971868.8804086,maxx=20037508.342789244,maxy=19971868.8804086))
		super(Grid3857, self).__init__(unit="m", bounds=BoundingBox(minx=-20037508.342789244,miny=-20037508.342789244,maxx=20037508.342789244,maxy=20037508.342789244))
	def validate(self, x, y, z):
		if x >= ceil(2**(z)):
			raise ValueError("x out of bounds: %d" % x)
		if y >= ceil(2**(z)):
			raise ValueError("y out of bounds: %d" % y)
		