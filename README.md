# Python Chess Game with Minimax AI (Threaded)

A fully functional **Chess game built using Python and Tkinter**, featuring:
- Two Player mode
- Single Player mode vs **AI (Minimax with Alpha-Beta Pruning)**
- Real-time **chess clocks**
- **Threaded AI computation** to keep the UI responsive
- Legal move validation and checkmate detection

This project demonstrates **game logic, AI algorithms, multithreading, and GUI development** in Python.

---

## Screenshots

### Menu
![Menu](https://github.com/Vaishuu-creator/Python-Chess-AI/blob/main/screenshots/menu.png)  

### Game Play
![Game play](https://github.com/Vaishuu-creator/Python-Chess-AI/blob/main/screenshots/gameplay.png)

---

## Project Overview

This Chess application allows users to play:
- **Player vs Player** (local)
- **Player vs AI** (Minimax-based opponent)

The AI uses:
- **Minimax algorithm**
- **Alpha-Beta pruning**
- Material-based board evaluation
- Move ordering for better performance

To ensure smooth gameplay, AI thinking runs in a **separate thread**, preventing UI freezing.

---

## Features

- Complete chess board with Unicode pieces
- AI opponent using Minimax + Alpha-Beta pruning
- Threaded AI processing (non-blocking UI)
- 10-minute chess timers for both players
- Legal move validation
- Check & checkmate detection
- Chess.com-style board colors and highlights
- Menu system to select game mode

---

## How It Works

1. User selects **game mode** (Two Player / AI)
2. White (lowercase pieces) always starts
3. Legal moves are calculated for selected pieces
4. Game state is updated after every move
5. In AI mode:
   - Board is evaluated using material values
   - Minimax searches the best move up to a fixed depth
   - Alpha-Beta pruning improves efficiency
   - AI move runs in a background thread
6. Game ends on:
   - Checkmate
   - Stalemate
   - Time expiration

---

## Technologies Used

- Python
- Tkinter (GUI)
- Minimax Algorithm
- Alpha-Beta Pruning
- Multithreading
- Object-Oriented Programming (OOP)

---

## Project Structure

Python-Chess-AI/  
│  
├── main.py - Complete chess game & AI logic  
├── README.md - Project documentation  
└── assets/ - (Optional) icons / screenshots  

---

## Installation & Setup

### 1️. Clone the Repository
    git clone https://github.com/Vaishuu-creator/Python-Chess-AI
    cd Python-Chess-AI

### 2️. Run the Game

    python main.py

No external libraries required  
Python 3.8+ recommended

---

## How to Play

1. Launch the game
2. Choose **Game Mode**:
    - Two Player
    - AI Opponent (Minimax)
3. Click a piece to see its **legal moves**
4. Click a highlighted square to move
5. Watch the clock — each player has **10 minutes**
6. Game ends on checkmate, stalemate, or time-out

---

## Game Rules

- White = lowercase pieces (human player)
- Black = uppercase pieces (AI or second player)
- Standard chess movement rules
- Illegal moves are automatically blocked
- King cannot move into check

---

## AI Details
### Evaluation Function

- Material-based scoring:
  - Pawn = 1
  - Knight/Bishop = 3
  - Rook = 5
  - Queen = 9
  - King = 200

### Search Algorithm

- Minimax with Alpha-Beta pruning
- Fixed search depth (configurable)
- Capture-priority move ordering

---

## Learning Outcomes

- Implementing Minimax AI
- Alpha-Beta pruning optimization
- Chess rules & state validation
- Multithreading in Python GUI apps
- Tkinter canvas-based rendering
- Timer & event-driven programming

---

## Future Enhancements

- Adjustable AI difficulty levels
- Piece animations
- Move history panel
- Sound effects
- PGN/FEN support
- Online multiplayer

---

## License

This project is licensed under the MIT License.

---

## Author

### Vaishali Murugesan
Final Year Computer Technology Student  
Aspiring AI / Software Engineer  

If you like this project, consider giving it a star!
