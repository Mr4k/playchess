var board, game = new Chess();

// do not pick up pieces if the game is over
// only pick up pieces for White
var onDragStart = function(source, piece, position, orientation) {
  if (game.in_checkmate() === true || game.in_draw() === true ||
    piece.search(/^w/) !== -1) {
    return false;
  }
};

var makeComputerMove = function() {
  //send an ajax request
  console.log("request sent")
  $.ajax({
      url: '/white_move',
      method: 'POST',
      data: JSON.stringify({fen : game.fen()}),
      contentType:"application/json",
      success: function(move) {
          console.log(move);
          game.move(move, {sloppy: true});
          //console.log(game.ascii())
          board.position(game.fen());
      }
  });
};

var onDrop = function(source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  });

  // illegal move
  if (move === null) return 'snapback';

  // ask server for best legal move for white
  window.setTimeout(makeComputerMove, 10);
};

// update the board position after the piece snap
// for castling, en passant, pawn promotion
var onSnapEnd = function() {
  board.position(game.fen());
};

var cfg = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd
};

board = ChessBoard('board', cfg);
window.setTimeout(makeComputerMove, 10);
//$("#board").append("<div class='loader'>Loading...</div>")