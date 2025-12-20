import tkinter as tk
import random
import time
import math
import threading

# ---------- CONFIG ----------
AI_DEPTH = 3  # minimax depth (increase to make AI stronger; will be slower)
# ----------------------------

# ---------- piece glyphs ----------
pieces = {
    'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
    'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙',
    '.': ''
}

start_board = [
    ['R','N','B','Q','K','B','N','R'],
    ['P','P','P','P','P','P','P','P'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['p','p','p','p','p','p','p','p'],
    ['r','n','b','q','k','b','n','r'],
]

# piece values for evaluation (positive for material)
PIECE_VALUES = {
    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 200
}

# ---------- Main Game Class ----------
class ChessGame:
    def __init__(self, root, mode='two'):
        """
        root: Tk root
        mode: 'two' for two-player, 'ai' for single-player vs AI
        """
        self.root = root
        self.mode = mode  # 'two' or 'ai'
        self.root.title("Chess - Minimax AI (Threaded)")

        # UI frames
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side='top', fill='x')

        self.info_label = tk.Label(self.top_frame, text="Mode: " + ("AI Opponent (Minimax)" if mode == 'ai' else "Two Player"))
        self.info_label.pack(side='left', padx=8)

        # AI thinking indicator
        self.ai_thinking_var = tk.StringVar(value="")
        tk.Label(self.top_frame, textvariable=self.ai_thinking_var, fg='blue').pack(side='left', padx=(8,10))

        # Timers
        self.timer_white_var = tk.StringVar(value="10:00")
        self.timer_black_var = tk.StringVar(value="10:00")
        tk.Label(self.top_frame, text="White (You)").pack(side='left', padx=(20,2))
        tk.Label(self.top_frame, textvariable=self.timer_white_var).pack(side='left', padx=(0,10))
        tk.Label(self.top_frame, text="Black (AI)" if mode=='ai' else "Black (Player)").pack(side='left', padx=(10,2))
        tk.Label(self.top_frame, textvariable=self.timer_black_var).pack(side='left', padx=(0,10))

        # Canvas (board)
        self.canvas = tk.Canvas(root, width=640, height=640)
        self.canvas.pack()

        # Game state
        self.cell_size = 80
        self.board = [row[:] for row in start_board]
        self.selected = None
        self.valid_moves = []
        self.turn = 'white'     # 'white' uses lowercase pieces (user)
        self.game_running = True

        # Timers in seconds
        self.remaining = {'white': 10 * 60, 'black': 10 * 60}  # 10 minutes each
        self._timer_job = None

        # AI state
        self.ai_thinking = False

        # Bind clicks
        self.canvas.bind("<Button-1>", self.click)

        # Draw initial
        self.draw_board()

        # start timer loop
        self.last_tick = time.time()
        self._tick()

    # ---------- drawing ----------
    def draw_board(self):
        self.canvas.delete("all")

        # Chess.com colors
        light = "#EEEED2"
        dark  = "#769656"
        highlight_move = "#BACA44"   # Chess.com style move highlight
        selected_sq = "#F6F669"      # Chess.com selected square

        for i in range(8):
            for j in range(8):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                base_color = light if (i + j) % 2 == 0 else dark

                # highlight precedence: selected square > valid moves > base color
                if self.selected == (i, j):
                    color = selected_sq
                elif (i, j) in self.valid_moves:
                    color = highlight_move
                else:
                    color = base_color

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')

                piece = self.board[i][j]
                if piece != '.':
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                            text=pieces[piece], font=("Arial", 44))

        # Optional: show whose turn in title
        self.root.title(f"Chess - {'White' if self.turn=='white' else 'Black'} to move - Mode: {'AI' if self.mode=='ai' else 'Two Player'}")

    # ---------- click handling ----------
    def click(self, event):
        # ignore clicks if game over or AI is thinking
        if not self.game_running or self.ai_thinking:
            return

        row, col = event.y // self.cell_size, event.x // self.cell_size

        # If a square outside board, ignore
        if not (0 <= row < 8 and 0 <= col < 8):
            return

        # If a move is selected previously
        if self.selected:
            if (row, col) in self.valid_moves:
                sr, sc = self.selected
                piece = self.board[sr][sc]

                # Make move
                self.board[row][col] = piece
                self.board[sr][sc] = '.'

                # After move, check for checkmate
                opponent = 'black' if self.turn == 'white' else 'white'
                if self.is_checkmate_board(self.board, opponent):
                    self.draw_board()
                    self.game_over(f"{self.turn.capitalize()} wins by checkmate!")
                    return

                # Switch turn
                self.turn = opponent
                self.selected = None
                self.valid_moves = []
                self.draw_board()

                # If AI mode and it's AI's turn, run AI in background thread
                if self.mode == 'ai' and self.turn == 'black' and self.game_running:
                    self.ai_thinking = True
                    self.ai_thinking_var.set("AI thinking...")
                    threading.Thread(target=self.ai_move_minimax_thread, daemon=True).start()
                return

            # else clear selection
            self.selected = None
            self.valid_moves = []
            self.draw_board()
            return

        # No previously selected piece: try to select
        piece = self.board[row][col]
        if piece != '.' and self.is_correct_turn(piece):
            self.selected = (row, col)
            self.valid_moves = self.get_legal_moves(r=row, c=col, board=self.board, turn=self.turn)
            self.draw_board()

    # mapping turn -> piece case (kept your convention)
    def is_correct_turn(self, piece):
        return (self.turn == 'white' and piece.islower()) or (self.turn == 'black' and piece.isupper())

    # ---------- Game over ----------
    def game_over(self, message):
        self.game_running = False
        self.canvas.unbind("<Button-1>")
        self.canvas.create_rectangle(0, 280, 640, 360, fill='black', stipple='gray50')
        self.canvas.create_text(320, 320, text=message, font=("Arial", 28), fill="red")

    # ---------- legal moves & move generation (board param) ----------
    def get_legal_moves(self, r, c, board=None, turn=None):
        """
        Returns list of (mr,mc) legal moves for piece at r,c on given board and turn.
        If board is None -> self.board. If turn is None -> self.turn.
        """
        if board is None:
            board = self.board
        if turn is None:
            turn = self.turn

        piece = board[r][c]
        moves = self.get_piece_moves(r, c, piece, board=board)
        legal = []
        for mr, mc in moves:
            temp = [row[:] for row in board]
            temp[mr][mc] = piece
            temp[r][c] = '.'
            if not self.in_check_board(temp, turn):
                legal.append((mr, mc))
        return legal

    def get_piece_moves(self, r, c, piece, board=None):
        if board is None:
            board = self.board

        directions = {
            'n': [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)],
            'b': [(-1,-1),(-1,1),(1,-1),(1,1)],
            'r': [(-1,0),(1,0),(0,-1),(0,1)],
            'q': [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)],
            'k': [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)],
        }

        moves = []
        if piece == '.':
            return moves

        is_white = piece.islower()
        p = piece.lower()

        def inside(x, y):
            return 0 <= x < 8 and 0 <= y < 8

        def add_move(x, y):
            if not inside(x, y):
                return False
            target = board[x][y]
            if target == '.' or (target.isupper() != piece.isupper()):
                moves.append((x, y))
                return target == '.'  # continue sliding only if empty
            return False

        if p == 'p':
            step = -1 if is_white else 1
            start_row = 6 if is_white else 1
            # forward
            if inside(r + step, c) and board[r + step][c] == '.':
                moves.append((r + step, c))
                if r == start_row and inside(r + 2*step, c) and board[r + 2*step][c] == '.':
                    moves.append((r + 2*step, c))
            # captures
            for dc in (-1, 1):
                nr, nc = r + step, c + dc
                if inside(nr, nc) and board[nr][nc] != '.' and (board[nr][nc].isupper() != piece.isupper()):
                    moves.append((nr, nc))

        elif p == 'n':
            for dr, dc in directions['n']:
                add_move(r + dr, c + dc)

        elif p in ('b', 'r', 'q'):
            for dr, dc in directions[p]:
                x, y = r + dr, c + dc
                while add_move(x, y):
                    x += dr
                    y += dc

        elif p == 'k':
            for dr, dc in directions['k']:
                add_move(r + dr, c + dc)

        return moves

    # ---------- find king ----------
    def find_king_board(self, board, color):
        king = 'k' if color == 'white' else 'K'
        for i in range(8):
            for j in range(8):
                if board[i][j] == king:
                    return (i, j)
        return None

    # ---------- check detection (board versions) ----------
    def in_check_board(self, board, color):
        king_pos = self.find_king_board(board, color)
        if king_pos is None:
            return True  # no king -> treat as in check

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == '.':
                    continue
                # Skip own pieces
                if (color == 'white' and piece.islower()) or (color == 'black' and piece.isupper()):
                    continue
                moves = self.get_piece_moves(r, c, piece, board=board)
                if king_pos in moves:
                    return True
        return False

    def is_checkmate_board(self, board, color):
        if not self.in_check_board(board, color):
            return False
        # iterate all pieces of color
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == '.':
                    continue
                # only consider pieces of `color`
                if (color == 'white' and piece.isupper()) or (color == 'black' and piece.islower()):
                    continue
                for mr, mc in self.get_piece_moves(r, c, piece, board=board):
                    temp = [row[:] for row in board]
                    temp[mr][mc] = piece
                    temp[r][c] = '.'
                    if not self.in_check_board(temp, color):
                        return False
        return True

    # ---------- Minimax & helpers ----------
    def evaluate_board(self, board):
        """
        Return evaluation from Black's perspective: positive -> Black advantage.
        """
        black_score = 0
        white_score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == '.':
                    continue
                val = PIECE_VALUES.get(piece.lower(), 0)
                if piece.isupper():
                    black_score += val
                else:
                    white_score += val
        return black_score - white_score

    def generate_all_legal_moves(self, board, color):
        """
        Return list of moves for color on board as [((r,c),(mr,mc)), ...]
        color: 'white' or 'black'
        """
        result = []
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == '.':
                    continue
                if color == 'white' and piece.isupper():
                    continue
                if color == 'black' and piece.islower():
                    continue
                legal = self.get_legal_moves(r, c, board=board, turn=color)
                for (mr, mc) in legal:
                    result.append(((r, c), (mr, mc)))
        return result

    def make_move_on_board(self, board, move):
        """
        Return a new board after applying move=((sr,sc),(tr,tc))
        """
        (sr, sc), (tr, tc) = move
        newb = [row[:] for row in board]
        newb[tr][tc] = newb[sr][sc]
        newb[sr][sc] = '.'
        return newb

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax with alpha-beta.
        maximizing_player: True when it's Black's turn (AI), False for White (human).
        Returns (best_value, best_move) where best_move is ((sr,sc),(tr,tc)) or None.
        """
        # Terminal checks: checkmates
        if self.is_checkmate_board(board, 'white'):
            return (10000, None)
        if self.is_checkmate_board(board, 'black'):
            return (-10000, None)

        # generate moves
        black_moves = self.generate_all_legal_moves(board, 'black')
        white_moves = self.generate_all_legal_moves(board, 'white')

        if depth == 0 or (not black_moves and not white_moves):
            return (self.evaluate_board(board), None)

        if maximizing_player:
            max_eval = -math.inf
            best_move = None
            moves = black_moves
            # simple ordering: prioritize captures
            def move_score(mv):
                (sr, sc), (tr, tc) = mv
                target = board[tr][tc]
                return PIECE_VALUES.get(target.lower(), 0)
            moves.sort(key=move_score, reverse=True)

            for mv in moves:
                newb = self.make_move_on_board(board, mv)
                val, _ = self.minimax(newb, depth-1, alpha, beta, False)
                if val > max_eval:
                    max_eval = val
                    best_move = mv
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return (max_eval, best_move)
        else:
            min_eval = math.inf
            best_move = None
            moves = white_moves
            def move_score(mv):
                (sr, sc), (tr, tc) = mv
                target = board[tr][tc]
                return PIECE_VALUES.get(target.lower(), 0)
            moves.sort(key=move_score, reverse=True)

            for mv in moves:
                newb = self.make_move_on_board(board, mv)
                val, _ = self.minimax(newb, depth-1, alpha, beta, True)
                if val < min_eval:
                    min_eval = val
                    best_move = mv
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return (min_eval, best_move)

    # ---------- AI thread entrypoint ----------
    def ai_move_minimax_thread(self):
        """
        This runs in a background thread. Compute best move (pure CPU work),
        then schedule the UI update on main thread via root.after.
        """
        if not self.game_running:
            self.ai_thinking = False
            self.ai_thinking_var.set("")
            return

        # compute best move using minimax on current board snapshot
        board_snapshot = [row[:] for row in self.board]
        val, best_move = self.minimax(board_snapshot, AI_DEPTH, -math.inf, math.inf, True)

        # fallback: if no move found, get legal moves
        if best_move is None:
            moves = self.generate_all_legal_moves(board_snapshot, 'black')
            if not moves:
                # schedule endgame handling on main thread
                self.root.after(0, lambda: self._handle_ai_no_moves(board_snapshot))
                return
            best_move = random.choice(moves)

        # schedule applying the move on the main thread
        self.root.after(0, lambda: self._apply_ai_move_from_thread(best_move))

    def _handle_ai_no_moves(self, board_snapshot):
        # called on main thread if AI had no moves
        if self.in_check_board(board_snapshot, 'black'):
            self.game_over("White wins by checkmate!")
        else:
            self.game_over("Stalemate!")
        self.ai_thinking = False
        self.ai_thinking_var.set("")

    def _apply_ai_move_from_thread(self, move):
        """
        Apply the AI move on the main thread (safe to touch UI).
        """
        if not self.game_running:
            self.ai_thinking = False
            self.ai_thinking_var.set("")
            return

        # make move
        self.board = self.make_move_on_board(self.board, move)

        # check for checkmate for opponent
        if self.is_checkmate_board(self.board, 'white'):
            self.draw_board()
            self.game_over("Black (AI) wins by checkmate!")
            self.ai_thinking = False
            self.ai_thinking_var.set("")
            return

        # switch turn back to white
        self.turn = 'white'
        self.selected = None
        self.valid_moves = []
        self.ai_thinking = False
        self.ai_thinking_var.set("")
        self.draw_board()

    # ---------- Timer handling ----------
    def _tick(self):
        """Called frequently with after to update timers."""
        if not self.game_running:
            return

        now = time.time()
        elapsed = now - getattr(self, 'last_tick', now)
        # decrement time in whole-second steps
        if elapsed >= 1.0:
            steps = int(elapsed)
            self.last_tick = now
            if self.turn in self.remaining:
                self.remaining[self.turn] -= steps
                if self.remaining[self.turn] < 0:
                    self.remaining[self.turn] = 0

                # update labels
                self.timer_white_var.set(self._format_time(self.remaining['white']))
                self.timer_black_var.set(self._format_time(self.remaining['black']))

                # if any reaches zero -> game over on time
                if self.remaining[self.turn] <= 0:
                    winner = 'black' if self.turn == 'white' else 'white'
                    msg = "White wins on time!" if winner == 'white' else "Black wins on time!"
                    self.game_over(msg)
                    return

        # schedule next tick
        self._timer_job = self.root.after(200, self._tick)

    def _format_time(self, secs):
        mins = secs // 60
        s = secs % 60
        return f"{int(mins):02d}:{int(s):02d}"

# ---------- Menu UI ----------
class Menu:
    def __init__(self, root):
        self.root = root
        self.mode_var = tk.StringVar(value='ai')  # default AI
        self.frame = tk.Frame(root)
        self.frame.pack(pady=30)

        tk.Label(self.frame, text="Chess - Choose Mode", font=("Arial", 16)).pack(pady=(0,10))

        tk.Radiobutton(self.frame, text="Two Player", variable=self.mode_var, value='two').pack(anchor='w')
        tk.Radiobutton(self.frame, text="AI Opponent (Minimax)", variable=self.mode_var, value='ai').pack(anchor='w')

        self.start_btn = tk.Button(self.frame, text="Start Game", width=20, command=self.start_game)
        self.start_btn.pack(pady=12)

        # optional: show instructions
        tk.Label(self.frame, text="Note: White = lowercase pieces (you). Timers: 10:00 each.").pack(pady=(8,0))

    def start_game(self):
        mode = self.mode_var.get()
        # remove menu
        self.frame.destroy()
        # create game
        ChessGame(self.root, mode=mode)


# ---------- run ----------
if __name__ == "__main__":
    root = tk.Tk()
    Menu(root)
    root.mainloop()
