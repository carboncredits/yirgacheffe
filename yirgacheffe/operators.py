from .window import Window

class LayerConstant:
	def __init__(self, val):
		self.val = val

	def __str__(self):
		return str(self.val)

	def _eval(self, index):
		return self.val


class LayerMathMixin:

	def __add__(self, other):
		return LayerOperation(self, "__add__", other)

	def __sub__(self, other):
		return LayerOperation(self, "__sub__", other)

	def __mul__(self, other):
		return LayerOperation(self, "__mul__", other)

	def __truediv__(self, other):
		return LayerOperation(self, "__truediv__", other)

	def __pow__(self, other):
		return LayerOperation(self, "__pow__", other)

	def _eval(self, index):
		window = self.window
		return self.read_array(0, index, window.xsize, 1)

	def apply(self, func, other=None):
		return LayerOperation(self, func, other)


class LayerOperation(LayerMathMixin):

	def __init__(self, lhs, op=None, rhs=None):
		self.lhs = lhs
		if op: self.op = op
		if rhs:
			if isinstance(rhs, int) or isinstance(rhs, float):
				self.rhs = LayerConstant(rhs)
			else:
				self.rhs = rhs

	def __str__(self):
		try:
			return f"({self.lhs} {self.op} {self.rhs})"
		except AttributeError:
			return str(self.lhs)

	def __len__(self):
		return len(self.lhs)

	@property
	def window(self) -> Window:
		try:
			return self.lhs.window
		except AttributeError:
			# If neither side had a window attribute then
			# the operation doesn't have anything useful to
			# say, so let the exception propegate up
			return self.rhs.window

	def _eval(self, yoffset):
		try:
			return getattr(self.lhs._eval(yoffset), self.op)(self.rhs._eval(yoffset))
		except TypeError: # op not a string
			try:
				return self.op(self.lhs._eval(yoffset), self.rhs._eval(yoffset))
			except AttributeError: # no rhs
				return self.op(self.lhs._eval(yoffset))
		except AttributeError: # no op attr
			window = self.lhs.window
			val = self.lhs.read_array(0, yoffset, window.xsize, 1)
			return val

	def save(self, band):
		window = self.window
		for yoffset in range(window.ysize):
			line = self._eval(yoffset)
			band.WriteArray(line, 0, yoffset)
