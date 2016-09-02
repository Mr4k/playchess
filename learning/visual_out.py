import numpy as np
from six.moves import cPickle
import chess

f = lambda x: np.unravel_index(x,(8,8,8,8))
g = lambda x: chr(x[0]+97)+str(x[1]+1)+chr(x[2]+97)+str(x[3]+1)
h = lambda x: g(f(int(x)))

def convert_input(input_):
    board = unfck_board(input_)
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

def unfck_output(output):
	out = []
	for line in output:
		k = 0
		m_out = []
		begun = False
		num = ""
		for i in xrange(2):
			while line[k] != ']':
				if line[k] == '(' and line[k+1] == '[':
					begun = True
					k+=1
				elif begun:
					num += line[k]
				k += 1
			m_out.append(float(num))
			k += 1
			begun = False
			num = ""
		out.append(tuple(m_out))
	return out

def unfck_board(f_board):
	board = chess.Board()
	board.clear()
	board.turn = chess.WHITE
	index = 0
	for square in chess.SQUARES:
		for i in xrange(6):
			if f_board[index+i] == 1:
				piece = chess.Piece(i + 1, f_board[index + 7])
				board.set_piece_at(square, piece)
				break
		index += 8
	return board

def test_legality(board, move):
	mv = chess.Move.from_uci(move)
	return board.is_pseudo_legal(mv)

def test_capture(board, move):
	mv = chess.Move.from_uci(move)
	return board.is_capture(mv)

def test_castle(board, move):
	mv = chess.Move.from_uci(move)
	return board.is_kingside_castling(mv) or board.is_queenside_castling(mv)

def main():
	moves, conf = zip(*unfck_output(open("train_guess.txt","r")))
	moves = map(h, moves)
	moves = zip(moves, conf)
	print str(len(moves)) + " Moves Chosen:"
	boards = map(unfck_board, np.ma.load("white-chess-testing-input.data"))
	move_board_pairs = zip(boards, moves)

	#various statistics about the moves the program makes
	legal_moves = 0
	captures = 0
	castles = 0
	for i in xrange(783):
		legality = test_legality(move_board_pairs[i][0], move_board_pairs[i][1][0])
		print "MOVE BOARD PAIR:"
		print "Board:"
		print move_board_pairs[i][0]
		print "Move:"
		print move_board_pairs[i][1]
		print "Legality:"
		
		print legality
		if legality:
			legal_moves += 1
			if test_capture(move_board_pairs[i][0], move_board_pairs[i][1][0]):
				print "Capture"
				captures += 1
			elif test_castle(move_board_pairs[i][0], move_board_pairs[i][1][0]):
				print "Castle"
				castles += 1
		print "FEN:"
		print move_board_pairs[i][0].fen()

	print str(legal_moves) + " Legal Moves"
	print str(captures) + " Legal Captures"
	print str(castles) + " Legal Castles"
	print str(len(set(zip(*moves)[0]))) + " Unique Moves:"
	print set(zip(*moves)[0])

if __name__ == "__main__":
	main()
	