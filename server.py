from flask import Flask
from flask import request
from lookahead.search import search_positions
from intuition.policy import get_next_move

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/white_move', methods=['POST'])
def white_move():
	print request.json['fen']
	print "search POS:"
	#print str(search_positions(request.json['fen']))
	return str(get_next_move(request.json['fen'], False))

@app.route('/black_move', methods=['POST'])
def black_move():
	print request.json['fen']
	print "search POS:"
	#print str(search_positions(request.json['fen']))
	return str(search_positions(request.json['fen']))

if __name__ == "__main__":
    app.run(debug = True)