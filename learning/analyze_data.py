import numpy as np
from six.moves import cPickle

data = np.squeeze(np.array(np.ma.load("white-chess-testing-output.data")))
output = map(lambda x:[np.array([np.argmax(x, axis=0)]), np.array([x[np.argmax(x, axis=0)]])],data)
for element in output:
	print element