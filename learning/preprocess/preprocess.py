import chess.pgn
import numpy as np
from six.moves import cPickle
from scipy.sparse import dok_matrix
from scipy.sparse import csc_matrix
import random

#preprocess training data
def convert_epd(epd):
	board = chess.Board(epd + " 0 1")
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

def export_training_data(data,name):
	random.shuffle(data)
	data_len = len(data)
	test_data = data[:max(int(data_len/200.0),1)]
	del data[:max(int(data_len/200.0),1)]
	print "Data Stats:"
	print data_len
	print len(data)
	print len(test_data)
	training_in, training_out = zip(*data)
	test_in, test_out = zip(*test_data)
	fout = open(name + '-training-input.data', 'w+b')
	cPickle.dump(training_in, fout, protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()
	fout = open(name + '-training-output.data', 'w+b')
	cPickle.dump(training_out, fout, protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()
	fout = open(name + '-testing-input.data', 'w+b')
	cPickle.dump(test_in, fout, protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()
	fout = open(name + '-testing-output.data', 'w+b')
	cPickle.dump(test_out, fout, protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()

def prune_data(position_dict):
	data = []
	for key in position_dict:
		if np.sum(np.sum(position_dict[key][:,0].todense())) > 3:
			data.append((convert_epd(key),normalize_probabilities(position_dict[key].todense())))
	print len(data)
	return data

def parse_game(game, position_dict):
	moves = []
	node = game.end()
	board = chess.Board()
	while node.parent is not None:
		moves.append(node.move)
		node = node.parent
	moves = reversed(moves)
	for move in moves:
		epd = board.epd()
		mv = convert_move(move)
		if board.turn == chess.BLACK:
			board.push(move)
			continue
		board.push(move)
		if epd not in position_dict:
			position_dict[epd] = dok_matrix((4096, 1), dtype=np.float)
		position_dict[epd][mv,0] += 1

def build_training_data(fname, position_dict, max_games = -1):
	#position_dict = [{},{}]
	fpgn = open(fname)
	game = chess.pgn.read_game(fpgn)
	games = 0
	while game is not None:
		games += 1
		parse_game(game, position_dict)
		if games % 1000 == 0:
			print games
		if games % 50000 == 0:
			export_training_data(prune_data(position_dict), "white-chess")
			#export_training_data(prune_data(position_dict[chess.WHITE]), "white-chess")
		if games == max_games:
			break
		game = chess.pgn.read_game(fpgn)
	return position_dict

if __name__ == '__main__':
	position_dict = {}
	print "Preprocessing..."
	build_training_data("KingBase/KingBase2016-03-B50-B99.pgn", position_dict, 2000000)
	build_training_data("KingBase/KingBase2016-03-C00-C19.pgn", position_dict, 2000000)
	build_training_data("KingBase/KingBase2016-03-C20-C59.pgn", position_dict, 2000000)
	build_training_data("KingBase/KingBase2016-03-C60-C99.pgn", position_dict, 2000000)
	build_training_data("KingBase/KingBase2016-03-D00-D29.pgn", position_dict, 2000000)
	export_training_data(prune_data(position_dict), "white-chess")
	#export_training_data(prune_data(position_dicts[chess.WHITE]), "white-chess")