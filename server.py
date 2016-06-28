from flask import Flask
from flask import request
from search import search_positions

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/move', methods=['POST'])
def move():
	print request.json['fen']
	print "search POS:"
	#print str(search_positions(request.json['fen']))
	return str(search_positions(request.json['fen']))

if __name__ == "__main__":
    app.run(debug = True)