import lasagne
import theano
import theano.tensor as T
import numpy as np
from six.moves import cPickle

#here's where shit gets funky
#a lot of these functions should be generalized
def convert_epd(epd):
	board = chess.Board(epd)
	output = []
	for square in chess.SQUARES:
		square_out = [0,0,0,0,0,0,0,0]
		piece = board.piece_at(square)
		if piece is not None:
			square_out[piece.piece_type - 1] = 1
			square_out[piece.color + 6] = 1
		output.extend(square_out)
	castling_rights = [0,0,0,0]
	for i in xrange(2):
		castling_rights[2 * i] = int(board.has_kingside_castling_rights(i))
		castling_rights[2 * i + 1] = int(board.has_queenside_castling_rights(i))
	output.extend(castling_rights)
	#either going to be from black or white's perspective constantly
	"""turns = [0, 0]
	turns[board.turn] = 1
	output.extend(turns)"""
	return np.array(output)

def convert_move(move):
	#converts a move of the form (old position)(new position) such as 'e2f1' to an index in a 4096(64x64) array
	str_mv = str(move)
	return np.ravel_multi_index((ord(str_mv[0])-ord('a'),int(str_mv[1]) - 1,ord(str_mv[2])-ord('a'),int(str_mv[3]) - 1),(8,8,8,8))

def normalize_probabilities(outcome):
	return outcome / float(np.sum(outcome))

def build_model(input_var):
    from lasagne.nonlinearities import leaky_rectify, softmax
    network = lasagne.layers.InputLayer((None, 516), input_var)
    network = lasagne.layers.DenseLayer(lasagne.layers.dropout(network, 0.2),
                                        1000, nonlinearity=leaky_rectify,W=lasagne.init.GlorotNormal(gain = 1.414142857))
    network = lasagne.layers.DenseLayer(lasagne.layers.dropout(network, 0.5),
                                        2000, nonlinearity=leaky_rectify,W=lasagne.init.GlorotNormal(gain = 1.414142857))
    network = lasagne.layers.DenseLayer(lasagne.layers.dropout(network, 0.5),
                                        2000, nonlinearity=leaky_rectify,W=lasagne.init.GlorotNormal(gain = 1.414142857))
    network = lasagne.layers.DenseLayer(lasagne.layers.dropout(network, 0.5),
                                        4096, nonlinearity=softmax)
    return network

def build_network_from_model(filename):
	input_var = T.matrix('X')
	network = build_model(input_var)
	with np.load('model.npz') as f:
		param_values = [f['arr_%d' % i] for i in range(len(f.files))]
	lasagne.layers.set_all_param_values(network, param_values)
	prediction = lasagne.layers.get_output(network, deterministic=True)
	prediction_fn = theano.function([input_var], prediction)
	return [network, input_var, prediction_fn]

def search_positions(network_tuple, fen):
	network = network_tuple[0]
	input_var = network_tuple[1]
	prediction = network_tuple[2]
	move_distribution = prediction_fn(convert_epd(fen))
	board = chess.Board(fen)
	move_distribution = normalize_probabilities(move_distribution[map(board.legal_moves,lambda x:convert_move(x.uci()))])
	return np.unravel_index(np.amax(move_distribution),(8,8,8,8))

	