import chess
from eval_pos import eval_pos

#basic minmax alpha beta pruning
def search_positions(fen):
	board = chess.Board(fen)
	#board test
	print board.turn
	largest = -10000
	best_move = "NONE"
	for move in board.legal_moves:
		print str("Move:(")+str(move)+str(")")
		val = search_board_min(board, move, 0, -100000, 100000, 6)
		if val > largest:
			best_move = move
			largest = val
	return best_move

def search_board_min(board, move_to, depth, alpha, beta, maxdepth):
	board.push(move_to)
	if board.is_checkmate():
		board.pop()
		return 1000
	if board.is_stalemate():
		board.pop()
		return 600
	if depth == maxdepth:
		val = eval_pos(board)
		board.pop()
		return val
	else:
		smallest = 10000
		for move in board.legal_moves:
			smallest = min(search_board_max(board, move, depth + 1, alpha, beta, maxdepth), smallest)
			alpha = smallest
			if smallest >= beta:
				board.pop()
				return smallest
		board.pop()
		return smallest

def search_board_max(board, move_to, depth, alpha, beta, maxdepth):
	board.push(move_to)
	if board.is_checkmate():
		board.pop()
		return 1000
	if board.is_stalemate():
		board.pop()
		return 200
	if depth == maxdepth:
		val = eval_pos(board)
		board.pop()
		return val
	else:
		largest = -10000
		for move in board.legal_moves:
			largest = max(search_board_min(board, move, depth + 1, alpha, beta, maxdepth), largest)
			beta = largest
			if largest <= alpha:
				board.pop()
				return largest
		board.pop()
		return largest

			