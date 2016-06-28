import chess
import random
from eval_pos import eval_pos

debug_nodes_visited = 0

#basic minmax alpha beta pruning
def search_positions(fen):
	global debug_nodes_visited
	board = chess.Board(fen)
	#board test
	print eval_pos(board)
	largest = -10000
	best_move = "NONE"
	debug_nodes_visited = 0
	beta = -100000
	alpha = 100000
	for move in board.legal_moves:
		print str("Move:(")+str(move)+str(")")
		val = search_board_min(board, move, 0, alpha, beta, 4)
		beta = max(val, beta)
		if val > largest:
			best_move = move
			largest = val
	print str(debug_nodes_visited)
	print largest
	return best_move


def search_board_min(board, move_to, depth, alpha, beta, maxdepth):
	global debug_nodes_visited
	debug_nodes_visited += 1;
	board.push(move_to)
	if board.is_checkmate():
		board.pop()
		return 1000
	if board.is_stalemate():
		board.pop()
		return 0
	if depth == maxdepth:
		val = eval_pos(board)
		board.pop()
		return val
	else:
		smallest = 10000
		for move in board.legal_moves:
			smallest = min(search_board_max(board, move, depth + 1, alpha, beta, maxdepth), smallest)
			alpha = min(smallest, alpha)
			if smallest <= beta:
				#print "pruned beta"
				board.pop()
				return beta
		board.pop()
		"""print "::Visiting Position(min)::"
		print board
		print "Score:" + str(smallest)"""
		return smallest

def search_board_max(board, move_to, depth, alpha, beta, maxdepth):
	global debug_nodes_visited
	debug_nodes_visited += 1;
	board.push(move_to)
	"""if board.fen() in transposition_table:
		return transposition_table[board.fen()]"""
	if board.is_checkmate():
		board.pop()
		return -1000
	if board.is_stalemate():
		board.pop()
		return 0
	if depth == maxdepth:
		val = eval_pos(board)
		board.pop()
		return val
	else:
		largest = -10000
		for move in board.legal_moves:
			largest = max(search_board_min(board, move, depth + 1, alpha, beta, maxdepth), largest)
			beta = max(largest, beta)
			if largest >= alpha:
				#print "pruned alpha"
				#transposition_table[board.fen()] = alpha
				board.pop()
				return alpha
		#transposition_table[board.fen()] = largest
		board.pop()
		"""print "::Visiting Position(max)::"
		print board
		print "Score:" + str(largest)"""
		return largest

			