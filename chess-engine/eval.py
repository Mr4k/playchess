import chess
import random

def eval_board(board):
	#can this beat Terrence?
	total = 0
	for piece in range(Chess.Pawn, Chess.Queen + 1):
		total += 0.1 * piece * len(board.pieces(piece, not board.turn))
	for piece in range(Chess.Pawn, Chess.Queen + 1):
		total -= 0.1 * piece * len(board.pieces(piece, board.turn))
	print total