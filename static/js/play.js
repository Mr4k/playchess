var board, game = new Chess();

// do not pick up pieces if the game is over
// only pick up pieces for White
var onDragStart = function(source, piece, position, orientation) {
  if (game.in_checkmate() === true || game.in_draw() === true ||
    piece.search(/^w/) !== -1) {
    return false;
  }
};

var makeComputerMove = function(side) {
  //send an ajax request
  console.log("request sent")
  console.log('/'+side+'_move')
  $.ajax({
      url: '/'+side+'_move',
      method: 'POST',
      data: JSON.stringify({fen : game.fen()}),
      contentType:"application/json",
      success: function(move) {
          console.log(move);
          game.move(move, {sloppy: true});
          //console.log(game.ascii())
          board.position(game.fen());
          if (game.in_checkmate() === true || game.in_draw() === true){
              console.log("stalled")
              return
            }
          if (side === 'white'){
            window.setTimeout(makeBlackMove, 10);
          } else {
            window.setTimeout(makeWhiteMove, 10);
          }
      }
  });
};

var makeWhiteMove = function(){
  makeComputerMove('white')
}

var makeBlackMove = function(){
  makeComputerMove('black')
}

var cfg = {
  draggable: false,
  position: 'start'
};

board = ChessBoard('board', cfg);
window.setTimeout(makeWhiteMove, 10);
//$("#board").append("<div class='loader'>Loading...</div>")