import chess
import random

piece_worth = [2, 7, 7, 14, 18, 24]
#total piece worth = 2*8+7*2+82+14*2+18+24

def eval_pos(board):
	#can this beat Terrence?
	total = 0
	for piece in range(chess.PAWN, chess.KING + 1):
		total += piece_worth[piece - 1] * len(board.pieces(piece, False))
		for p in board.pieces(piece, False):
			total += 0.01 * len(board.attackers(False, p)) * piece_worth[piece - 1]
	for piece in range(chess.PAWN, chess.KING + 1):
		total -= piece_worth[piece - 1] * len(board.pieces(piece, True))
		for p in board.pieces(piece, True):
			total += 0.01 * len(board.attackers(False, p)) * piece_worth[piece - 1]

	return total