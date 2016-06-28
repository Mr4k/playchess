import chess

#basic minmax alpha beta pruning
def search_positions(fen):
	pass
def search_board(board, depth, alpha, beta, maxdepth):
	for move in board.legal_moves():
		print move