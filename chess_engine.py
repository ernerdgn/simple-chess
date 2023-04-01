"""
this part will store infos of the current state of the game and determining the best possible move
and saving the move log.
"""
class gamestate():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

        self.white_to_move = True
        self.move_log = []
        self.move_border_low = 1
        self.move_border_high = 8
        
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        
        #for valid moves algorithm #1
        # self.check_mate = False
        # self.stale_mate = False

        #for valid moves algorithm #2
        self.in_check = False
        self.pins = []
        self.checks = []

    """
    basic moving function, cant work for castling, en-passant and pawn promotion
    """

    def make_move(self, move):
        self.board[move.start_r][move.start_c] = "--"
        self.board[move.end_r][move.end_c] = move.moved_piece
        self.move_log.append(move) #logging the move, it provides to undo
        self.white_to_move = not self.white_to_move #switching the player turn
        if move.moved_piece == "wK":  #tracking king's location
            self.white_king_location = (move.end_r, move.end_c)
        elif move.moved_piece == "bK":
            self.black_king_location = (move.end_r, move.end_c)


    """
    Undo
    """
    def undo_move(self):
        if len(self.move_log) != 0:  #there must be a move to undo
            move = self.move_log.pop()
            self.board[move.start_r][move.start_c] = move.moved_piece
            self.board[move.end_r][move.end_c] = move.captured_piece
            self.white_to_move = not self.white_to_move
            if move.moved_piece == "wK":  #tracking king's location
                self.white_king_location = (move.start_r, move.start_c)
            elif move.moved_piece == "bK":
                self.black_king_location = (move.start_r, move.start_c)

    """
    moves WITH check checking
    """
    def get_valid_moves(self):
        ########################################## ALGORITHM 1 ##########################################
        # #=============================================================#
        # # algorithm for get_valid_moves()
        # # 1- Generate all the possible moves
        # # 2- For each move, make the move
        # # 3- Generate all opponent's moves
        # # 4- For each opponent move, seek for the checks
        # # 5- If check, move is not valid
        
        # # 1
        # moves = self.get_all_possible_moves()
        # # 2
        # for i in range(len(moves) - 1, -1, -1):  # going backwards to eliminate index change based errors
        #     self.make_move(moves[i])  #(C)
        #     # 3 and 4
        #     self.white_to_move = not self.white_to_move  #switching the turns because make_move switchted (C)
        #     if self.in_check():
        #         # 5
        #         moves.remove(moves[i])  #removing invalid move from the list
        #     self.white_to_move = not self.white_to_move  #(C)
        #     self.undo_move()  #(C)
        # #=============================================================#
        # if len(moves) == 0:  #checkmate/stalemate
        #     if self.in_check():
        #         self.check_mate = True
        #     else:
        #         self.stale_mate = True
        # else:
        #     self.stale_mate = False
        #     self.check_mate = False

        # return moves
        ################################### END OF ALGORITHM 1 ##########################################

        ########################################## ALGORITHM 2 ##########################################
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:  # getting king locations
            king_r = self.white_king_location[0]
            king_c = self.white_king_location[1]
        else:
            king_r = self.black_king_location[0]
            king_c = self.black_king_location[1]
        if self.in_check:  #if current player in check
            if len(self.checks) == 1:  #if current player's king is threatened by one enemy piece
                moves = self.get_all_possible_moves()
                #to block, move a piece on to squares between enemy piece and the king
                check = self.checks[0]  #check data
                check_r = check[0]  #checking piece location
                check_c = check[1]
                piece_checking = self.board[check_r][check_c]
                valid_squares = []  #squares that pieces can move to
                if piece_checking[1] == "N":  #if threatening piece is a knight, move the king or capture the knight
                    valid_squares = [(check_r, check_c)]  ##there
                else:
                    for i in range(self.move_border_low, self.move_border_high):
                        valid_square = (king_r + check[2] * i, king_c + check[3] * i)  #check[i](i = 2 or 3) is check direction
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_r and valid_square[1] == check_c:  #when checking piece is eaten...
                            break  #...end check 
                #get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].moved_piece[1] != "K":  #move doesnt move king so it must block or capture
                        if not (moves[i].end_r, moves[i].end_c) in valid_squares:  #move doesn't block check or captured piece
                            moves.remove(moves[i])
            else:  #double check, so king has to move
                self.get_king_moves(king_r, king_c, moves)
        else: #not in check, so all moves are valid
            moves = self.get_all_possible_moves()

        return moves
        ################################### END OF ALGORITHM 2 ##########################################

########################################### ALGORITHM 1 #########################################
####################################### Helper function(s) ######################################
    # """
    # to see if current player is in check
    # """
    # def in_check(self):
    #     if self.white_to_move:
    #         return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
    #     else:
    #         return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    # """
    # determine if the enemy can attack the corresponding square
    # """
    # def square_under_attack(self, r, c):
    #     self.white_to_move = not self.white_to_move  #switch to opponents POV
    #     opponent_moves = self.get_all_possible_moves()
    #     self.white_to_move = not self.white_to_move  #switch turns back
    #     for move in opponent_moves:
    #         if move.end_r == r and move.end_c == c:  #square is under attack
    #             #self.white_to_move = not self.white_to_move
    #             return True
    #     return False    
####################################### END OF ALGORITHM 1 ######################################
####################################### Helper function(s) ######################################

########################################### ALGORITHM 2 #########################################
####################################### Helper function(s) ######################################
    """
    returns if the current player is checked, a list of pins and a list of checks (for double check)
    """
    def check_for_pins_and_checks(self):
        pins = []  #pinned ally piece location and direction of the pinning enemy piece
        checks = []  #checking enemy pieces locations
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_r = self.white_king_location[0]
            start_c = self.black_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_r = self.black_king_location[0]
            start_c = self.black_king_location[1]
        #check outward from king for pins and checks, keep track of pins
        #directionss = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        #directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
                        #index: [0,3]   [4,7]
                        #piece: rook    bishop
        for i in range(len(directions)):
            direction = directions[i]
            possible_pin = ()  #reset possible pins
            for j in range(self.move_border_low, self.move_border_high):
                end_r = start_r + direction[0] * j
                end_c = start_c + direction[1] * j
                if 0 <= end_r < 8 and 0 <= end_c < 8:
                    end_piece = self.board[end_r][end_c]
                    if end_piece[0] == ally_color and end_piece[1] != "K":  #THIS IS SOMETHING FUNNY
                        if possible_pin == ():  #first ally piece on the line could be pinned
                            possible_pin = (end_r, end_c, direction[0], direction[1])
                        else:  #if there's a second ally piece on the line, no pin or check possible on this line
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 1- Orthogonally away from the king and piece is rook
                        # 2- Diagonally away from the king and piece is bishop
                        # 3- One square away from the king and piece is pawn
                        # 4- Any direction and piece is queen
                        # 5- Any direction one square away and piece is king (necessary to prevent side by side kings)
                        if (0 <= i <= 3 and type == "R") or \
                            (4 <= i <= 7 and type == "B") or \
                            (j == 1 and type == "p" and ((enemy_color == "w" and 6 <= i <= 7) or (enemy_color == "b" and 4 <= i <= 5))) or \
                            (type == "Q") or (j == 1 and type == "K"):            #6-7                                    4-5
                            if possible_pin == ():  #no piece blocking so check is true
                                in_check = True
                                print("CHECK")
                                checks.append((end_r, end_c, direction[0], direction[1]))
                                print(checks)
                                break
                            else:  #two ally pieces on the line, so pin is false
                                pins.append(possible_pin)
                                break
                        else:  #enemy piece blocking, so pin is false
                            break
                else:  #off board
                    break
        #knight checks
        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        for knight_move in knight_moves:
            end_r = start_r + knight_move[0]
            end_c = start_c + knight_move[1]
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  #enemy knight attacking the king
                    in_check = True
                    checks.append((end_r, end_c, knight_move[0], knight_move[1]))
            # else:  #off board
            #     break
        return in_check, pins, checks
####################################### END OF ALGORITHM 2 ######################################
####################################### Helper function(s) ######################################

    """
    all moves without legal move filtering
    """
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  #number of rows
            for c in range(len(self.board[r])):  #number of columns in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  #calls the appropriate move function based on piece type
        return moves

########################################### ALGORITHM 1 #########################################
######################################### Move functions ########################################
    # """
    # get all pawn moves for the pawn located at the row and column and add this moves on the list
    # """
    # def get_pawn_moves(self, r, c, moves):
    #     # WHITE PAWNS
    #     if self.white_to_move:
    #         if self.board[r-1][c] == "--":  #one square move
    #             moves.append(Move((r, c),(r-1, c), self.board))
    #             if r==6 and self.board[r-2][c] == "--":
    #                 moves.append(Move((r, c), (r-2, c), self.board))
    #         #capturing pieces
    #         if c-1 >= 0:  #captures left
    #             if self.board[r-1][c-1][0] == "b":  #a black piece to capture for white pawns
    #                 moves.append(Move((r, c), (r-1, c-1), self.board))
    #         if c+1 <= 7:  #captures right
    #             if self.board[r-1][c+1][0] == "b":
    #                 moves.append(Move((r, c), (r-1, c+1), self.board))
    #     # BLACK PAWNS
    #     elif self.white_to_move == False:
    #         if self.board[r+1][c] == "--":
    #             moves.append(Move((r, c), (r+1, c), self.board))
    #             if r==1 and self.board[r+2][c] == "--":
    #                 moves.append(Move((r, c), (r + 2, c), self.board))
    #         #capturing pieces
    #         if c-1 >= 0: #capturing left
    #             if self.board[r+1][c-1][0] == "w":
    #                 moves.append(Move((r, c), (r+1, c-1), self.board))
    #         if c+1 <= 7:  #capturing right
    #             if self.board[r+1][c+1][0] == "w":
    #                 moves.append(Move((r, c), (r+1, c+1), self.board))

    # """
    # get all rook moves for the rook located at the row and column and add this moves on the list
    # """

    # def get_rook_moves(self, r, c, moves):
    #     rook_directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  #up,left,down,right
    #     enemy_piece = "b" if self.white_to_move else "w"
    #     # if self.white_to_move:
    #     #     enemy_piece = "b"
    #     # else:
    #     #     enemy_piece = "w"  #LINE ABOVE IS THE SHORT WAY FOR 2 CONDITION IF BLOCKS

    #     for direction in rook_directions:
    #         for a in range(self.move_border_low, self.move_border_high):
    #             end_row = r + direction[0] * a
    #             end_column = c + direction[1] * a  #because of the zeros in directions move will be linear (only x and y axis)
    #             if 0 <= end_row < 8 and 0 <= end_column < 8:  #in board borders
    #                 end_piece = self.board[end_row][end_column]
    #                 if end_piece == "--":  #if you want to take rook to an empty square
    #                     moves.append(Move((r, c), (end_row, end_column), self.board))
    #                 elif end_piece[0] == enemy_piece:  #enemy capture and self piece block
    #                     moves.append(Move((r, c), (end_row, end_column), self.board))
    #                     break  #CRITIC if this break doesnt exist, pieces can capture pieces behind the enemy pieces
    #                 else:  #friendly piece block
    #                     break
    #             else:  #not on board
    #                 break

    # """
    # get all bishop moves for the bishop located at the row and column and add this moves on the list
    # """

    # def get_bishop_moves(self, r, c, moves):
    #     bishop_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    #                         #northwest northeast southwest southeast
    #     enemy_piece = "b" if self.white_to_move else "w"
    #     for direction in bishop_directions:
    #         for a in range(self.move_border_low,self.move_border_high):
    #             end_row = r + direction[0] * a
    #             end_column = c + direction[1] * a
    #             if 0 <= end_row < 8 and 0 <= end_column < 8:
    #                 end_piece = self.board[end_row][end_column]
    #                 if end_piece == "--":
    #                     moves.append(Move((r,c), (end_row, end_column), self.board))
    #                 elif end_piece[0] == enemy_piece:
    #                     moves.append(Move((r,c), (end_row, end_column), self.board))
    #                     break
    #                 else:
    #                     break
    #             else:
    #                 break
    

    # """
    # get all queen moves for the queen located at the row and column and add this moves on the list
    # """

    # def get_queen_moves(self, r, c, moves):
    #     self.get_rook_moves(r,c,moves)
    #     self.get_bishop_moves(r,c,moves)


    # """
    # get all knight moves for the knight located at the row and column and add this moves on the list
    # """

    # def get_knight_moves(self, r, c, moves):
    #     knight_directions = ((-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1))
    #     #enemy_piece = "b" if self.white_to_move else "w"
    #     ally_piece = "w" if self.white_to_move else "b"
    #     for direction in knight_directions:
    #         end_row = r + direction[0]
    #         end_column = c + direction[1]
    #         if 0 <= end_row < 8 and 0 <= end_column < 8:
    #             end_piece = self.board[end_row][end_column]
    #             if end_piece[0] != ally_piece:
    #                 moves.append(Move((r,c), (end_row,end_column), self.board))
    #         #     if end_piece == "--":
    #         #         moves.append(Move((r,c), (end_row, end_column), self.board))
    #         #     elif end_piece[0] == enemy_piece:
    #         #         moves.append(Move((r,c), (end_row, end_column), self.board))
    #         #     else:
    #         #         break
    #         # else:
    #         #     break


    # """
    # get all king moves for the king located at the row and column and add this moves on the list
    # """

    # def get_king_moves(self, r, c, moves):
    #     self.move_border_high = 2  #make the coefficient a = 1 (look for bishop and rook move functions)
    #     self.get_rook_moves(r,c,moves)
    #     self.get_bishop_moves(r,c,moves)
    #     self.move_border_high = 8
    #     # king_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
    #     #                    #northwest northeast southwest southeast north  west   south    east
    #     # enemy_piece = "b" if self.white_to_move else "w"
    #     # for direction in king_directions:
    #     #     # for a in range(1, 8):
    #     #     #     end_row = r + direction[0] * a
    #     #     #     end_column = c + direction[1] * a
    #     #     end_row = r + direction[0]
    #     #     end_column = c + direction[1]
    #     #     if 0 <= end_row < 8 and 0 <= end_column < 8:
    #     #         end_piece = self.board[end_row][end_column]
    #     #         if end_piece == "--":
    #     #             moves.append(Move((r,c), (end_row, end_column), self.board))
    #     #         elif end_piece[0] == enemy_piece:
    #     #             moves.append(Move((r,c), (end_row, end_column), self.board))
    #     #         else:
    #     #             break
    #     #     else:
    #     #         break
#################################### END OF ALGORITHM 1 #########################################
###################################### Move functions ###########################################

########################################### ALGORITHM 2 #########################################
######################################### Move functions ########################################
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins) - 1, -1, -1):  #check if the piece is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break  #if it is, do not let the player make the move

        if self.white_to_move:  # WHITE PAWN MOVES
            if self.board[r-1][c] == "--":  #one square move
                if not piece_pinned or pin_dir == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":  #two square, as opening move
                        moves.append(Move((r, c), (r-2, c), self.board))
            #capturing
            if c-1 >= 0:  #capturing left
                if self.board[r-1][c-1][0] == "b":
                    if not piece_pinned or pin_dir == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:  #capturing right
                if self.board[r-1][c+1][0] == "b":
                    if not piece_pinned or pin_dir == (-1, 1):
                        moves.append(Move((r,c), (r-1, c+1), self.board))

        else:  # BLACK PAWN MOVES
            if self.board[r+1][c] == "--":  #one square move
                if not piece_pinned or pin_dir == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  #two square, as opening move
                        moves.append(Move((r, c), (r+2, c), self.board))
            #capturing
            if c-1 >= 0:  #capturing left
                if self.board[r+1][c-1][0] == "w":
                    if not piece_pinned or pin_dir == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:  #capturing right
                if self.board[r+1][c+1][0] == "w":
                    if not piece_pinned or pin_dir == (1, 1):
                        moves.append(Move((r,c), (r+1, c+1), self.board))
    
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins) - 1, -1, -1):  #check if the piece is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  #not able to move queen from pin on rook moves
                    self.pins.remove(self.pins[i])
                break  #if it is, do not let the player make the move
        
        rook_directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemy_piece = "b" if self.white_to_move else "w"
        for direction in rook_directions:
            for i in range(self.move_border_low, self.move_border_high):
                end_r = r + direction[0] * i
                end_c = c + direction[1] * i
                if 0 <= end_r < 8 and 0 <= end_c < 8:
                    if not piece_pinned or pin_dir == direction or pin_dir == (-direction[0], -direction[1]):
                                    #pinned pieces must be able to move both ways in the pinned line (↑)
                        end_piece = self.board[end_r][end_c]
                        if end_piece == "--":
                            moves.append(Move((r,c), (end_r, end_c), self.board))
                        elif end_piece[0] == enemy_piece:
                            moves.append(Move((r,c), (end_r, end_c), self.board))
                            break
                        else:
                            break
                else:
                    break
                        

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins) - 1, -1, -1):  #check if the piece is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break  #if it is, do not let the player make the move

        bishop_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_piece = "b" if self.white_to_move else "w"
        for direction in bishop_directions:
            for i in range(self.move_border_low, self.move_border_high):
                end_r = r + direction[0] * i
                end_c = c + direction[1] * i
                if 0 <= end_r < 8 and 0 <= end_c < 8:
                    if not piece_pinned or pin_dir == direction or pin_dir == (-direction[0], -direction[1]):
                        end_piece = self.board[end_r][end_c]
                        if end_piece == "--":
                            moves.append(Move((r,c), (end_r, end_c), self.board))
                        elif end_piece[0] == enemy_piece:
                            moves.append(Move((r,c), (end_r, end_c), self.board))
                            break
                        else:
                            break
                else:
                    break
                        
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins) - 1, -1, -1):  #check if the piece is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                #pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break  #if it is, do not let the player make the move

        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        ally_color = "w" if self.white_to_move else "b"
        for move in knight_moves:
            end_r = r + move[0]
            end_c = c + move[1]
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                if not piece_pinned:
                    end_piece = self.board[end_r][end_c]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r,c), (end_r, end_c), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        column_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(self.move_border_high):
            end_r = r + row_moves[i]
            end_c = c + column_moves[i]
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece[0] != ally_color:
                    #place king and check for the checks
                    if ally_color == "w":
                        self.white_king_location = (end_r, end_c)
                    else:
                        self.black_king_location = (end_r, end_c)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r,c), (end_r, end_c), self.board))
                        print("move happend")
                    #placing king back to origin location
                    if ally_color == "w":
                        self.white_king_location = (r, c)
                        print("get back")
                    else:
                        self.black_king_location = (r, c)

#################################### END OF ALGORITHM 2 #########################################
###################################### Move functions ###########################################

class Move():
    #maps keys to value --- (rank file notation)
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_r = start_square[0]
        self.start_c = start_square[1]
        self.end_r = end_square[0]
        self.end_c = end_square[1]
        self.moved_piece = board[self.start_r][self.start_c]
        self.captured_piece = board[self.end_r][self.end_c]
        self.move_id = self.start_r * 1000 + self.start_c * 100 + self.end_r * 10 + self.end_c
        print(self.move_id)

    """
    overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_r, self.start_c) + self.get_rank_file(self.end_r, self.end_c)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
