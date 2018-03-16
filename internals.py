import copy
from collections import defaultdict
import engine
import threading

class Piece(object):
    """
    Class for the pieces in the game.
    """

    def __init__(self, color, kind):

        # Piece's player.
        self.color = color

        # The type of the piece.
        # King, Bishop etc.
        self.kind = kind

        # The last move of the piece
        # (from_tile, played_turn_num)
        self.last_move = None


class Board(object):
    """
    The class for the chessboard.
    """

    def __init__(self, debug=0):

        self.debug = debug
        self.debug_output("Board object created with the debug level {0}.".format(self.debug), 1)

        self.grid = [[None] * 8 for _ in range(8)]  # Empty Board

        # A square is marked after a pawn moves double,
        # marked square is the one behind the moved pawn.
        self.en_passant_square = None

        # Define piece lists of each color, order is important.
        self.white_pieces = [
            Piece("white", "rook"),
            Piece("white", "knight"),
            Piece("white", "bishop"),
            Piece("white", "queen"),
            Piece("white", "king"),
            Piece("white", "bishop"),
            Piece("white", "knight"),
            Piece("white", "rook")
        ]

        for i in range(8):
            self.white_pieces.append(Piece("white", "pawn"))

        self.black_pieces = [
            Piece("black", "rook"),
            Piece("black", "knight"),
            Piece("black", "bishop"),
            Piece("black", "queen"),
            Piece("black", "king"),
            Piece("black", "bishop"),
            Piece("black", "knight"),
            Piece("black", "rook")
        ]

        for i in range(8):
            self.black_pieces.append(Piece("black", "pawn"))

        # Filling the board with pieces.
        for col, piece in enumerate(self.white_pieces[:8]):
            self.grid[7][col] = piece
            self.grid[6][col] = self.white_pieces[col + 8]  # pawns

        for col, piece in enumerate(self.black_pieces[:8]):
            self.grid[0][col] = piece
            self.grid[1][col] = self.black_pieces[col + 8]  # pawns

    def get_moves(self, pos):
        """
        Get possible moves of a single piece.
        Unlegal moves resulting in a threat for the king are included
        in the result.
        """

        self.debug_output("get_moves called.", 5)

        moves = set()
        row, col = pos
        piece = self.grid[row][col]

        # Directions packed in lists
        # For the search function
        # Each direction (y, x):
        #  y = -1 means piece goes up, y = 1 means piece goes down, y = 0 means row is constant.
        #  x = -1 means piece goes left, x = 1 means piece goes right, x = 0 means col is constant.

        bishop_move = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        rook_move = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        queen_move = bishop_move + rook_move

        if piece.kind == "king":
            # The king moves like the queen, except the search length is 1.
            moves = self.direction_search(pos, queen_move, 1)

            # Check if the king can castle kingside.
            # First condition is the king is not under attack
            # Second condition is the king and the rook is not moved yet.
            opponent = "white" if piece.color == "black" else "black"
            if not self.king_under_attack(piece.color) and piece.last_move == None and self.grid[row][col + 3]:
                if self.grid[row][col + 3].last_move == None:
                    tiles_between = self.direction_search(pos, [(0, 1)], 2)

                    # Third rule is there should be no pieces between the king and the rook (length must be 2)
                    # Fourth rule is any of these tiles should not be attacked by any of the opponent's pieces
                    # Used set intersection for the fourth rule
                    if len(tiles_between) == 2 and not tiles_between.intersection(self.get_all_attacks(opponent)):
                        moves.add((row, col + 2))

                # Check if the king can castle queenside.
                # Same rules as above.
            if not self.king_under_attack(piece.color) and piece.last_move == None and self.grid[row][col - 4]:
                if self.grid[row][col - 4].last_move == None:
                    tiles_between = self.direction_search(pos, [(0, -1)], 3)
                    # Tiles king pass should have search length two.
                    # That is why it is calculated again.
                    tiles_king_pass = self.direction_search(pos, [(0, -1)], 2)

                    if len(tiles_between) == 3 and not tiles_king_pass.intersection(self.get_all_attacks(opponent)):
                        moves.add((row, col - 2))                   

        elif piece.kind == "queen":
            moves = self.direction_search(pos, queen_move, 7)

        elif piece.kind == "bishop":
            moves = self.direction_search(pos, bishop_move, 7)

        elif piece.kind == "knight":
            # All the possible moves of a knight.
            move_list = [(row - 2, col - 1),
                         (row - 2, col + 1),
                         (row - 1, col + 2),
                         (row + 1, col + 2),
                         (row + 2, col + 1),
                         (row + 2, col - 1),
                         (row + 1, col - 2),
                         (row - 1, col - 2)]

            # Add them if they are in the board
            for move in move_list:
                if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                    i, j = move
                    if not self.grid[i][j]:
                        moves.add(move) 

        elif piece.kind == "rook":
            moves = self.direction_search(pos, rook_move, 7)

        elif piece.kind == "pawn":
            
            if piece.color == "white":
                if row == 6:
                    # Move of the white pawn is -1, 0 because it goes up.
                    moves = self.direction_search(pos, [(-1, 0)], 2)
                else:
                    moves = self.direction_search(pos, [(-1, 0)], 1)

                    if self.en_passant_square in [(row - 1, col - 1), (row - 1, col + 1)]:
                        moves.add(self.en_passant_square)

            elif piece.color == "black":
                if row == 1:
                    moves = self.direction_search(pos, [(1, 0)], 2)

                else:
                    moves = self.direction_search(pos, [(1, 0)], 1)
                    
                    if self.en_passant_square in [(row + 1, col - 1), (row + 1, col - 1)]:
                        moves.add(self.en_passant_square)

        # Add attacked tiles with opponent pieces inside to legal moves.
        for tile in self.get_attacks(pos):
            i, j = tile
            if self.grid[i][j] and self.grid[i][j].color != piece.color:
                    moves.add((i, j))

        # This part will be handled in get_all_legal_moves function.
        # Not required anymore.
        """
        if self.kind == "king":
            if self.color == "white":
                moves = moves - self.get_all_attacks("black")
            elif self.color == "black":
                moves = moves - self.get_all_attacks("white")
        """

        return moves

    def get_all_moves(self, color):
        """
        The method that returns all the possible moves of a particular player
        (Including non-legal moves).
        """

        self.debug_output("get_all_moves called.", 4)

        moves = defaultdict(list)

        for i, row in enumerate(self.grid):
            for j, piece in enumerate(row):
                if piece and piece.color == color:
                    for move in self.get_moves((i, j)):
                        moves[(i, j)].append(move)

        return moves

    def get_all_legal_moves(self, color):
        """
        Try all possible moves of a player, return only the legal ones.
        """

        self.debug_output("get_all_legal_moves called.", 3)

        legal_moves = defaultdict(list)
        all_moves = self.get_all_moves(color)

        # Try all moves, append them to the result list if they are legal.
        for from_tile in all_moves:
            for to_tile in all_moves[from_tile]:
                if self.assume_move([from_tile, to_tile], color):
                    legal_moves[from_tile].append(to_tile)

        
        return legal_moves  

    def get_attacks(self, pos):
        """
        The method to get attacked tiles by a single particular piece.
        """

        self.debug_output("get_attacks called.", 5)

        tiles = set()
        row, col = pos
        piece = self.grid[row][col]

        # Directions packed in lists
        # For the search function

        bishop_move = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        rook_move = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        queen_move = bishop_move + rook_move

        if piece.kind == "king":
            # The king attacks like the queen, except the search length is 1.
            tiles = self.direction_search(pos, queen_move, 1, True)

        elif piece.kind == "queen":
            tiles = self.direction_search(pos, queen_move, 7, True)

        elif piece.kind == "bishop":
            tiles = self.direction_search(pos, bishop_move, 7, True)

        elif piece.kind == "knight":

            # All the possible moves of a knight.
            move_list = [(row - 2, col - 1),
                         (row - 2, col + 1),
                         (row - 1, col + 2),
                         (row + 1, col + 2),
                         (row + 2, col + 1),
                         (row + 2, col - 1),
                         (row + 1, col - 2),
                         (row - 1, col - 2)]

            # Add them if they are in the board
            for move in move_list:
                if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                    tiles.add(move) 

        elif piece.kind == "rook":
            tiles = self.direction_search(pos, rook_move, 7, True)

        elif piece.kind == "pawn":
            if piece.color == "white":
                if col > 0:
                    tiles.add((row - 1, col - 1))
                if col < 7:
                    tiles.add((row - 1, col + 1))

            elif piece.color == "black":
                if col > 0:
                    tiles.add((row + 1, col - 1))
                if col < 7:
                    tiles.add((row + 1, col + 1))

        return tiles

    def get_all_attacks(self, color):
        """
        The method to get all the attacked tiles by the given player.
        """

        self.debug_output("get_attacks called.", 3)

        tiles = set()

        for i, row in enumerate(self.grid):
            for j, tile in enumerate(row):

                # If there is a piece in the tile
                if tile:
                    # After finding a piece inside that tile,
                    # the tile is actually the piece itself.
                    # Imagine continuing as tile == piece

                    if tile.color == color:
                        tiles = tiles.union(self.get_attacks((i, j)))

        return tiles

    def assume_move(self, move, color):
        """
        The method that assumes a move is played, to check if it is a legal move.
        Hence, if a move puts the king in danger, that move is not legal. Also, 
        if a king is under attack and a move does not remove the attack, that 
        move is discarded too.
        """

        self.debug_output("assume_move called.", 2)

        # Copy the board instance
        # All the movement operations will be done
        # on the copied board.

        board_copy = copy.deepcopy(self) 

        from_tile, to_tile = move

        # promote=pawn is used for representing a pseudo-promote move,
        # when only assuming and testing.
        board_copy.make_move(from_tile, to_tile, promote="pawn")

        if board_copy.king_under_attack(color):
            return False # King is still under attack after the move.
        else:
            return True # The move helps the given king out of check.

    def make_move(self, from_tile, to_tile, promote="pawn"):
        """
        The method that handles piece alterations to apply a move.
        """

        self.debug_output("make_move called.", 2)
        
        fr, fc = from_tile
        tr, tc = to_tile

        piece = self.grid[fr][fc]
        piece.last_move = from_tile

        # Boolean value set true if a pawn went
        # two squares in the current move.
        pawn_double_moved = False

        # Detect castling.
        if piece.kind == "king":
            # Queenside
            if fc - tc == 2:
                self.debug_output("Castled Queenside.", 3)
                castle = self.grid[fr][0]
                self.grid[fr][0] = 0
                self.grid[fr][fc] = 0
                self.grid[tr][tc] = piece
                self.grid[fr][3] = castle       
            # Kingside
            elif tc - fc == 2:
                self.debug_output("Castled Kingside.", 3)
                castle = self.grid[fr][7]
                self.grid[fr][7] = 0
                self.grid[fr][fc] = 0
                self.grid[tr][tc] = piece
                self.grid[fr][5] = castle
            else:
                # Regular king move
                self.grid[fr][fc] = 0
                self.grid[tr][tc] = piece 

        # Detect promotion and en_passant.
        elif piece.kind == "pawn":
            
            if piece.color == "white":
                # If move is en_passant
                if to_tile == self.en_passant_square:
                    self.debug_output("White pawn at {0} made en_passant to {1}".format(from_tile, to_tile), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr + 1][tc] = 0
                    self.grid[tr][tc] = piece
                # If move is promotion
                elif tr == 0:
                    self.debug_output("White pawn at {0} made promotion to {1}, became a {2}".format(from_tile, to_tile, promote), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = Piece("white", promote)
                # If move is double pawn start
                elif fr == 6 and tr == 4:
                    self.debug_output("White pawn at {0} made double move to {1}, the next en_passant square is {2}".format(from_tile, to_tile, (tr + 1, tc)), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = piece
                    self.en_passant_square = (tr + 1, tc)
                    pawn_double_moved = True
                else:
                    self.debug_output("White pawn at {0} made move to {1}".format(from_tile, to_tile), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = piece


            elif piece.color == "black":
                # If move is en_passant
                if to_tile == self.en_passant_square:
                    self.debug_output("Black pawn at {0} made en_passant to {1}".format(from_tile, to_tile), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr - 1][tc] = 0
                    self.grid[tr][tc] = piece
                # If move is promotion
                elif tr == 7:
                    self.debug_output("Black pawn at {0} made promotion to {1}, became a {2}".format(from_tile, to_tile, promote), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = Piece("black", promote)
                # If move is double pawn start
                elif fr == 1 and tr == 3:
                    self.debug_output("Black pawn at {0} made double move to {1}, the next en_passant square is {2}".format(from_tile, to_tile, (tr - 1, tc)), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = piece
                    self.en_passant_square = (tr - 1, tc)
                    pawn_double_moved = True
                else:
                    self.debug_output("Black pawn at {0} made move to {1}".format(from_tile, to_tile), 3)
                    self.grid[fr][fc] = 0
                    self.grid[tr][tc] = piece

        else:
            self.grid[fr][fc] = 0
            self.grid[tr][tc] = piece

        # If a pawn did not move double in this turn,
        # reset en passant square.
        if not pawn_double_moved:
            self.en_passant_square = None

    def king_position(self, color):
        """
        Method that returns the king's position in the given color
        """

        self.debug_output("king_position called.", 4)

        for i, row in enumerate(self.grid):
            for j, tile in enumerate(row):
                # tile is a piece if filled.
                if tile and tile.color == color and tile.kind == "king":
                    return (i, j)

    def king_under_attack(self, color):
        """
        Method that returns if the king in the given color is under attack.
        """

        self.debug_output("king_under_attack called.", 4)

        if color == "white" and self.king_position("white") in self.get_all_attacks("black"):
            return True

        elif color == "black" and self.king_position("black") in self.get_all_attacks("white"):
            return True

        else:
            return False

    def direction_search(self, pos, directions, search_distance, inclusive = False):
        """
        Function to search all the empty tiles along a direction from a starting tile.
        """

        self.debug_output("direction_search called.", 4)

        tiles = set()
        
        row, col = pos
        piece = self.grid[row][col]

        # Search all directions given.
        for direction in directions:
            x, y = direction

            try:

                    # Search until another piece is detected or gone out of the board
                    # or the search distance is exhausted.

                    for i in range(1, search_distance + 1):
                        m, n = row + x*i, col + y*i # The direction
                        in_tile = self.grid[m][n] # The piece in that tile
                        if in_tile or not (0 <= m <= 7 and 0 <= n <= 7):

                            # The mechanics of pawn is different.
                            if piece.kind != "pawn":
                                # Add the piece detected in the path regardless of the color, if search is inclusive.
                                if inclusive and 0 <= m <= 7 and 0 <= n <= 7:
                                    tiles.add((m, n))

                            # Stop looking after a piece detected in the way.
                            break
                        tiles.add((m, n))

            except IndexError:
                # If it gives index error, it means the next tile in the search direction is out of the board.
                # Therefore the search skips to next direction.
                continue

        return tiles

    def print_board(self):
        """
        Method that prints the board to the console as an 
        formatted list.
        """

        for row in self.grid:
            for piece in row:
                if piece:
                    print((piece.color + " " + piece.kind).center(12), end=' ')
                else:
                    print("0".center(12), end=' ')
            print("\n")
        print("\n" + 12 * 8 * "-" + "\n")

    def debug_output(self, message, debug_level):
        if debug_level <= self.debug:
            print("[BOARD] " + message)

    @staticmethod
    def pos_to_square(pos):

        square = ""

        square += "abcdefgh"[pos[1]]
        square += "12345678"[7 - pos[0]]

        return square

    @staticmethod
    def square_to_pos(square):

        pos = (7 - "12345678".index(square[1]), "abcdefgh".index(square[0]))
        return pos

    @staticmethod
    def piece_to_letter(piece):
        letter = piece.kind[0] if piece.kind != "knight" else "n"
        if piece.color == "white":
            letter = letter.upper()
        return letter

    def produce_fen_position(self):

        position = ""

        # Preparing position part of the fen.
        for row in self.grid:
            empties = 0
            for piece in row:
                if piece:

                    if empties: position += str(empties)
                    position += Board.piece_to_letter(piece)
                    empties = 0

                else:
                    empties += 1

            if empties:
                position += str(empties)

            position += "/"
            empties = 0

        return position[:-1]

    def produce_fen_castling(self):

        # Preparing castling part
        castling = ""

        # If the piece at (7, 4) never moved before (white king)

        if self.grid[7][4].last_move == None:

            # Use the get moves function to see if the king
            # has the castling square in it's moves.
            if self.grid[7][6].last_move == None:
                castling += "K"
            if self.grid[7][1].last_move == None:
                castling += "Q"

        if self.grid[0][4].last_move == None:  
            if self.grid[0][6].last_move == None:
                castling += "k"
            if self.grid[7][1].last_move == None:
                castling += "q"
      
        return castling


class Game(object):

    def __init__(self, debug, game_mode):

        self.board = Board(debug)

        self.game_mode = game_mode

        self.chess_engine = engine.Engine()
        self.search_thread_running = False

        self.turn = "white"
        self.move_count = 1

        self.all_moves = []

        self.selected = None
        self.selected_moves = []

        self.best_move = None
        self.best_move_string = ""

        self.player_points = {
            "white": 1,
            "black": -1
        } 
    def move(self, from_tile, to_tile):


        self.board.make_move(from_tile, to_tile)
        self.all_moves.append(Board.pos_to_square(from_tile) + Board.pos_to_square(to_tile))
        self.turn = "white" if self.turn == "black" else "black"

        self.chess_engine.set_position(self.all_moves)
        
        if self.game_mode == "ai":
            

            move = self.chess_engine.get_best_move()

            from_square, to_square = move[:2], move[2:]
            from_pos, to_pos = Board.square_to_pos(from_square), Board.square_to_pos(to_square)

            if self.board.grid[from_pos[0]][from_pos[1]].color != self.turn:
                print ("Engine tried an illegal move.")

            self.board.make_move(from_pos, to_pos)
            self.all_moves.append(Board.pos_to_square(from_pos) + Board.pos_to_square(to_pos))
            self.turn = "white" if self.turn == "black" else "black"

            self.chess_engine.set_position(self.all_moves)


    def set_selection(self, pos):
        """
        Sets the list of moves which can be done by the selected piece.
        """

        self.selected = pos
        self.selected_moves = self.board.get_all_legal_moves(self.turn)[pos]

    def remove_selection(self):
        
        self.selected = None
        self.selected_moves = []

    def set_best_move(self):
        move = self.chess_engine.get_best_move()

        from_square, to_square = move[:2], move[2:]
        from_pos, to_pos = self.board.square_to_pos(from_square), self.board.square_to_pos(to_square)

        self.move(from_pos, to_pos)
        #self.best_move = from_pos, to_pos

    def search_best_move(self):
        self.search_thread_running = True
        self.search_thread = threading.Thread(target=self._search_best_move)
        self.search_thread.daemon = True
        self.search_thread.start()

    def _search_best_move(self):

        info_values = self.chess_engine.start_infinite_search()
        for info in info_values:
            if "pv" in info:
                self.best_move = Board.square_to_pos(info["pv"][0][:2]), Board.square_to_pos(info["pv"][0][2:4])

                self.best_move_string= str(info["pv"][0]) + " " + "%+.3f" % (self.player_points[self.turn] * info["score"]["cp"] / 100) + "(Depth " + str(info["depth"]) + ")" 
        #print("Analysis is ended.")
        self.best_move = None
        self.best_move_string = ""

    def stop_search(self):
        self.search_thread_running = False
        self.chess_engine.stop_infinite_search()
    
    def game_exit(self):
        self.search_thread_running = False
        self.chess_engine.stop_process()

    def produce_fen(self):
        pass

if __name__ == "__main__":
    b = Board(1)
