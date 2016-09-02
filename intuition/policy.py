import lasagne
import theano
import theano.tensor as T
import numpy as np
from six.moves import cPickle
import chess
import random
from lasagne.layers import InputLayer, DenseLayer, Conv2DLayer, batch_norm, ElemwiseSumLayer

#here's where shit gets funky
#a lot of these functions should be generalized
def convert_epd(epd, flip = False):
    board = chess.Board(epd)
    layers = np.zeros((6,8,8))
    for piece_type in xrange(1,6):
    	for sq in board.pieces(piece_type, chess.BLACK):
    		sq_x = sq % 8
    		sq_y = int(sq / 8)
    		layers[piece_type, sq_x, sq_y] = -1

    	for sq in board.pieces(piece_type, chess.WHITE):
    		sq_x = sq % 8
    		sq_y = int(sq / 8)
    		layers[piece_type, sq_x, sq_y] = 1
    return layers

def convert_move(move):
	#converts a move of the form (old position)(new position) such as 'e2f1' to an index in a 4096(64x64) array
	str_mv = str(move)
	return np.ravel_multi_index((ord(str_mv[0])-ord('a'),int(str_mv[1]) - 1,ord(str_mv[2])-ord('a'),int(str_mv[3]) - 1),(8,8,8,8))

def flip_move(move):
	return move[0] + str(9 - int(move[1])) + move[2] + str(9 - int(move[3]))

def normalize_probabilities(outcome):
	return outcome / float(np.sum(outcome))

def build_model(input_var):
    from lasagne.nonlinearities import leaky_rectify, softmax
    network = lasagne.layers.InputLayer(shape=(None, 6, 8, 8),
                                        input_var=input_var)
    network = Conv2DLayer(network, 16, 7, stride = 1, pad = 'same')
    network = build_residual_layer(network, 16, 2)
    network = build_resize_layer(network, 32)
    network = build_residual_layer(network, 32, 2)
    network = build_resize_layer(network, 64)
    network = build_residual_layer(network, 64, 2)
    network = build_resize_layer(network, 128)
    network = build_residual_layer(network, 128, 2)
    #network = DenseLayer(network, 128 * 64)
    network = DenseLayer(lasagne.layers.DropoutLayer(network, 0.2), 4096, nonlinearity=softmax)
    return network

def build_network_from_model(filename):
	input_var = T.tensor4('X')
	network = build_model(input_var)
	with np.load(filename) as f:
		param_values = [f['arr_%d' % i] for i in range(len(f.files))]
	lasagne.layers.set_all_param_values(network, param_values)
	prediction = lasagne.layers.get_output(network, deterministic=True)
	prediction_fn = theano.function([input_var], prediction)
	return [network, input_var, prediction_fn]

def build_residual_layer(network, num_filters, num_elements):
    original = network
    #like an 8x8 but with about half the parameters... maybe...
    for i in xrange(num_elements):
        network = Conv2DLayer(network, num_filters, 7, stride = 1, pad='same')
        network = batch_norm(network)
    return ElemwiseSumLayer([original, network])

def build_resize_layer(network, num_filters_out):
    #1x1 convolutions
    network = Conv2DLayer(network, num_filters_out, 1, stride = 1, pad='same')
    network = batch_norm(network)
    return network


def softmax(in_vec):
	vec = in_vec - np.max(in_vec)
	e = np.exp(vec)
	return e/np.sum(e)

def get_next_move(fen, flipped):
	board = chess.Board(fen)
	moves, intuition_prob = get_moves(board, 1, False)
	#return moves[0]
	#values = []
	#for move in moves:
		#print move
		#values.append(search_board_max(board, chess.Move.from_uci(move), 0, 100000, -100000, 2))
	#values = np.array(values)
	#come up with probabilty distribution based on value estimate (use softmax)
	#val_prob = softmax(-values)
	#final_prob = normalize_probabilities(val_prob)
	return np.random.choice(moves, 1, True)

def get_moves(board, num_moves, flip = False):
	#flip code
	if not flip:
		g = lambda x: chr(x[0]+97)+str(x[1]+1)+chr(x[2]+97)+str(x[3]+1)
	else:
		g = lambda x: flip_move(chr(x[0]+97)+str(x[1]+1)+chr(x[2]+97)+str(x[3]+1))

	network_tuple = build_network_from_model("conv-model.npz")
	network = network_tuple[0]
	input_var = network_tuple[1]
	prediction_fn = network_tuple[2]
	move_distribution = prediction_fn(np.expand_dims(convert_epd(board.fen(), True), axis = 0))
	#print g(np.unravel_index(np.argmax(move_distribution),(8,8,8,8)))
	new_move_distribution = np.zeros(4096)
	num_moves = min(len(board.legal_moves), num_moves)
	if not flip:
		legal_indices = map(lambda x:convert_move(x.uci()), board.legal_moves)
	else:
		legal_indices = map(lambda x:convert_move(flip_move(x.uci())), board.legal_moves)
	new_move_distribution[legal_indices] = move_distribution[0, legal_indices]
	best_moves = np.argpartition(-new_move_distribution, num_moves)
	return [map(lambda x: g(np.unravel_index(x,(8,8,8,8))), best_moves[:num_moves]), normalize_probabilities(new_move_distribution[best_moves[:num_moves]])]

	