# Quadtris Implementation

## Overview

Quadtris is a falling block puzzle game implemented using the Procedures, Tables, and Functions architecture. Players manipulate falling tetrominoes (4-block pieces) to create complete horizontal lines, which are then cleared for points. The game increases in difficulty as players progress through levels.

---

## Game Mechanics

- **Piece Movement**: Active tetromino falls automatically and can be moved left/right by player
- **Rotation**: Pieces can be rotated 90 degrees clockwise or counterclockwise
- **Line Clearing**: Complete horizontal rows are removed and award points
- **Gravity**: Pieces fall at increasing speeds as level increases
- **Lock Delay**: Brief pause before piece locks to allow last-moment adjustments
- **Next Piece**: Preview of upcoming pieces shown to player
- **Scoring**: Points awarded for line clears, with bonuses for multiple lines at once

---

## Data Structures

```c
void Setup();
void Loop();

struct ActivePiece { 
    int type;           // 0-6: I, O, T, S, Z, J, L
    int rotation;       // 0-3: rotation state
    float x;            // grid x position (can be fractional during movement)
    float y;            // grid y position (can be fractional during fall)
    int grid_x;         // snapped grid x position
    int grid_y;         // snapped grid y position
    int locked;         // 1 if piece is locked to grid
};

struct Grid { 
    int cells[20][10];  // 20 rows x 10 columns, 0=empty, 1-7=piece type
    int width; 
    int height; 
};

struct NextPieces { 
    int queue[3];       // next 3 pieces
    int count; 
};

struct Score { 
    int points; 
    int lines; 
    int level; 
    int highScore; 
};

struct GameState { 
    int state;          // 0=menu, 1=playing, 2=paused, 3=game_over
    float dropTimer;    // time until next auto-drop
    float dropSpeed;    // seconds between drops
    float lockTimer;    // time before piece locks
    int canHold;        // whether hold piece action is available
    int heldPiece;      // type of held piece, -1 if none
};

ActivePiece active_piece, active_piece_next;
Grid grid, grid_next;
NextPieces next_pieces, next_pieces_next;
Score score, score_next;
GameState game_state, game_state_next;

int main() {
  Setup();
  while (true) {
    Loop();
  }
}

void Setup() {
  InitActivePiece();
  InitGrid();
  InitNextPieces();
  InitScore();
  InitGameState();
}

void Loop() {
  UpdateGameState();
  ProcessInput();
  UpdateDropTimer();
  MoveActivePiece();
  RotateActivePiece();
  CheckCollision();
  LockPiece();
  ClearLines();
  SpawnNewPiece();
  UpdateScore();
  CheckGameOver();
}
```

---

## Tables

### ActivePiece
- **Columns**: 
  - type (int) - Piece type: 0=I, 1=O, 2=T, 3=S, 4=Z, 5=J, 6=L
  - rotation (int) - Current rotation state (0-3)
  - x (float) - Continuous x position for smooth movement
  - y (float) - Continuous y position for smooth falling
  - grid_x (int) - Snapped grid x coordinate
  - grid_y (int) - Snapped grid y coordinate
  - locked (int) - Whether piece is locked (1) or active (0)

### Grid
- **Columns**: 
  - cells (2D array) - Grid state, 0=empty, 1-7=filled with piece type
  - width (int) - Grid width (typically 10)
  - height (int) - Grid height (typically 20)

### NextPieces
- **Columns**: 
  - queue (array) - Upcoming piece types
  - count (int) - Number of pieces in preview (typically 3)

### Score
- **Columns**: 
  - points (int) - Current score
  - lines (int) - Total lines cleared
  - level (int) - Current level (affects drop speed)
  - highScore (int) - Best score achieved

### GameState
- **Columns**: 
  - state (int) - Current state: 0=menu, 1=playing, 2=paused, 3=game_over
  - dropTimer (float) - Time accumulated toward next auto-drop
  - dropSpeed (float) - Seconds between automatic drops
  - lockTimer (float) - Time before active piece locks to grid
  - canHold (int) - Whether hold action is available (1) or used (0)
  - heldPiece (int) - Type of held piece, or -1 if no piece held

---

## Procedures

### Setup
- **Tables**: ActivePiece, Grid, NextPieces, Score, GameState
- **Functions**: InitActivePiece, InitGrid, InitNextPieces, InitScore, InitGameState

### Loop
- **Tables**: ActivePiece, Grid, NextPieces, Score, GameState
- **Functions**: UpdateGameState, ProcessInput, UpdateDropTimer, MoveActivePiece, RotateActivePiece, CheckCollision, LockPiece, ClearLines, SpawnNewPiece, UpdateScore, CheckGameOver

### Individual Procedures

- **InitActivePiece**
  - Tables: ActivePiece
  - Purpose: Create first piece at spawn location
  
- **InitGrid**
  - Tables: Grid
  - Purpose: Initialize empty 20x10 grid
  
- **InitNextPieces**
  - Tables: NextPieces
  - Purpose: Generate initial queue of random pieces
  
- **InitScore**
  - Tables: Score
  - Purpose: Set initial score, lines, and level to 0/1
  
- **InitGameState**
  - Tables: GameState
  - Purpose: Set state to menu, initialize timers and drop speed
  
- **UpdateGameState**
  - Tables: GameState
  - Purpose: Update timers, handle state transitions
  
- **ProcessInput**
  - Tables: ActivePiece, GameState
  - Purpose: Handle player input for movement, rotation, hold, hard drop
  
- **UpdateDropTimer**
  - Tables: GameState
  - Purpose: Increment drop timer based on delta time
  
- **MoveActivePiece**
  - Tables: ActivePiece, GameState
  - Purpose: Move piece down when drop timer expires, or left/right from input
  
- **RotateActivePiece**
  - Tables: ActivePiece
  - Purpose: Rotate piece with wall kicks if needed
  
- **CheckCollision**
  - Tables: ActivePiece, Grid
  - Purpose: Detect if piece overlaps grid or boundaries
  
- **LockPiece**
  - Tables: ActivePiece, Grid, GameState
  - Purpose: Transfer piece blocks to grid when locked
  
- **ClearLines**
  - Tables: Grid, Score
  - Purpose: Find and remove complete lines, shift rows down
  
- **SpawnNewPiece**
  - Tables: ActivePiece, NextPieces, GameState
  - Purpose: Create new active piece from queue, refill queue
  
- **UpdateScore**
  - Tables: Score, GameState
  - Purpose: Award points for lines cleared, advance level
  
- **CheckGameOver**
  - Tables: Grid, ActivePiece, GameState
  - Purpose: Check if new piece spawns on occupied cells

---

## Functions

### Initialization Functions

#### InitActivePiece
- **Input Tables**: none
- **Output Tables**: ActivePiece
- **Body**: Creates first piece of random type at spawn position (x=3, y=0), rotation 0, not locked

#### InitGrid
- **Input Tables**: none
- **Output Tables**: Grid
- **Body**: Sets all cells to 0 (empty), width to 10, height to 20

#### InitNextPieces
- **Input Tables**: none
- **Output Tables**: NextPieces
- **Body**: Generates 3 random piece types using 7-bag randomizer algorithm

#### InitScore
- **Input Tables**: none
- **Output Tables**: Score
- **Body**: Sets points to 0, lines to 0, level to 1, loads high score

#### InitGameState
- **Input Tables**: none
- **Output Tables**: GameState
- **Body**: Sets state to 0 (menu), dropSpeed based on level 1, dropTimer to 0, lockTimer to 0, canHold to 1, heldPiece to -1

### Game Loop Functions

#### UpdateGameState
- **Input Tables**: GameState
- **Output Tables**: GameState
- **Body**: Handles pause/unpause, updates drop speed based on level

#### ProcessInput
- **Input Tables**: ActivePiece, GameState
- **Output Tables**: ActivePiece, GameState
- **Body**: Reads keyboard input for left/right movement, rotation (Z/X or arrows), hold (C or Shift), hard drop (Space)

#### UpdateDropTimer
- **Input Tables**: GameState
- **Output Tables**: GameState
- **Body**: Increments dropTimer by deltaTime, resets when exceeds dropSpeed

#### MoveActivePiece
- **Input Tables**: ActivePiece, GameState
- **Output Tables**: ActivePiece, GameState
- **Body**: Moves piece down if dropTimer triggered, applies horizontal movement from input, updates grid positions

#### RotateActivePiece
- **Input Tables**: ActivePiece
- **Output Tables**: ActivePiece
- **Body**: Changes rotation state (0-3), applies wall kick offsets if needed (SRS system)

#### CheckCollision
- **Input Tables**: ActivePiece, Grid
- **Output Tables**: ActivePiece
- **Body**: Tests if current piece position/rotation overlaps filled cells or boundaries, marks collision flag

#### LockPiece
- **Input Tables**: ActivePiece, Grid, GameState
- **Output Tables**: Grid, GameState, ActivePiece
- **Body**: If piece can't move down and lockTimer expires, copy piece blocks to grid cells with piece type

#### ClearLines
- **Input Tables**: Grid, Score
- **Output Tables**: Grid, Score
- **Body**: Scans for complete rows, removes them, shifts upper rows down, counts lines cleared

#### SpawnNewPiece
- **Input Tables**: ActivePiece, NextPieces, GameState
- **Output Tables**: ActivePiece, NextPieces, GameState
- **Body**: Takes first piece from queue, creates new ActivePiece, generates new random piece for end of queue, resets lockTimer and canHold

#### UpdateScore
- **Input Tables**: Score, GameState
- **Output Tables**: Score, GameState
- **Body**: Awards points based on lines cleared (1=100, 2=300, 3=500, 4=800), updates level every 10 lines, adjusts drop speed

#### CheckGameOver
- **Input Tables**: Grid, ActivePiece, GameState
- **Output Tables**: GameState
- **Body**: If newly spawned piece collides immediately, set state to game_over

---

## Threading Tables Through Functions

To thread tables through functions while maintaining high-level modularity (drag-and-drop reordering), you must decouple the **Logic Definition** (the pure function) from the **Data Wiring** (the generated glue code).

The architecture relies on three distinct layers:

1. **The State Container:** Holds the canonical version of all Tables (Current and Next).
2. **The Pure Core:** Functions that calculate logic without knowing about the game loop.
3. **The Generated Wrappers:** The bridge that "threads" the global state into the pure core.

### 1. The State Container (Memory)

To enable reordering and double buffering, the data must exist outside the functions. Use a global structure in the generated C code that holds two copies of every table: `_curr` (Read-Only during loop) and `_next` (Write-Only during loop).

```c
// Generated global state
ActivePiece active_piece_curr, active_piece_next;
Grid grid_curr, grid_next;
NextPieces next_pieces_curr, next_pieces_next;
Score score_curr, score_next;
GameState game_state_curr, game_state_next;
```

### 2. The Pure Core (User-Defined Logic)

Each function is written in its pure form, accepting input tables as parameters and returning output tables:

```c
ActivePiece MoveActivePiece_Pure(ActivePiece piece, GameState state) {
    ActivePiece result = piece;
    if (state.dropTimer >= state.dropSpeed) {
        result.y += 1.0;
        result.grid_y = (int)result.y;
    }
    return result;
}

Grid LockPiece_Pure(ActivePiece piece, Grid grid) {
    Grid result = grid;
    if (piece.locked) {
        int blocks[4][2];
        GetPieceBlocks(piece.type, piece.rotation, blocks);
        for (int i = 0; i < 4; i++) {
            int x = piece.grid_x + blocks[i][0];
            int y = piece.grid_y + blocks[i][1];
            if (y >= 0 && y < grid.height && x >= 0 && x < grid.width) {
                result.cells[y][x] = piece.type + 1;
            }
        }
    }
    return result;
}
```

### 3. The Generated Wrappers (Glue Code)

The code generator creates wrappers that read from `_curr` and write to `_next`:

```c
void MoveActivePiece_Wrapper() {
    active_piece_next = MoveActivePiece_Pure(active_piece_curr, game_state_curr);
}

void LockPiece_Wrapper() {
    grid_next = LockPiece_Pure(active_piece_next, grid_curr);
}
```

### The Loop (Generated)

The main loop is generated based on the procedure definitions:

```c
void Loop() {
    // Execute functions in order
    UpdateGameState_Wrapper();
    ProcessInput_Wrapper();
    UpdateDropTimer_Wrapper();
    MoveActivePiece_Wrapper();
    RotateActivePiece_Wrapper();
    CheckCollision_Wrapper();
    LockPiece_Wrapper();
    ClearLines_Wrapper();
    SpawnNewPiece_Wrapper();
    UpdateScore_Wrapper();
    CheckGameOver_Wrapper();
    
    // Commit next state to current
    active_piece_curr = active_piece_next;
    grid_curr = grid_next;
    next_pieces_curr = next_pieces_next;
    score_curr = score_next;
    game_state_curr = game_state_next;
}
```

---

## Key Design Benefits

1. **Modularity**: Each function is a pure transformation
2. **Reorderability**: Functions can be rearranged without breaking logic
3. **Testability**: Pure functions are easy to unit test
4. **Debugging**: State transitions are explicit and traceable
5. **Concurrency**: Double buffering prevents race conditions
6. **Code Generation**: Most boilerplate can be auto-generated from YAML

---

## Implementation Notes

### Tetromino Definitions

Define piece shapes using 4x4 grids for each rotation state:

```c
// I piece rotations (cyan)
int I_PIECE[4][4][4] = {
    {{0,0,0,0}, {1,1,1,1}, {0,0,0,0}, {0,0,0,0}},  // rotation 0
    {{0,0,1,0}, {0,0,1,0}, {0,0,1,0}, {0,0,1,0}},  // rotation 1
    {{0,0,0,0}, {0,0,0,0}, {1,1,1,1}, {0,0,0,0}},  // rotation 2
    {{0,1,0,0}, {0,1,0,0}, {0,1,0,0}, {0,1,0,0}}   // rotation 3
};

// O piece (yellow) - same for all rotations
int O_PIECE[4][4][4] = {
    {{0,1,1,0}, {0,1,1,0}, {0,0,0,0}, {0,0,0,0}},
    {{0,1,1,0}, {0,1,1,0}, {0,0,0,0}, {0,0,0,0}},
    {{0,1,1,0}, {0,1,1,0}, {0,0,0,0}, {0,0,0,0}},
    {{0,1,1,0}, {0,1,1,0}, {0,0,0,0}, {0,0,0,0}}
};

// ... T, S, Z, J, L pieces similarly defined
```

### Super Rotation System (SRS)

Implement wall kicks for rotation using offset tables:

```c
// Wall kick offsets for J, L, S, T, Z pieces
int WALL_KICKS[4][5][2] = {
    {{0,0}, {-1,0}, {-1,1}, {0,-2}, {-1,-2}},  // 0->1
    {{0,0}, {1,0}, {1,-1}, {0,2}, {1,2}},      // 1->2
    {{0,0}, {1,0}, {1,1}, {0,-2}, {1,-2}},     // 2->3
    {{0,0}, {-1,0}, {-1,-1}, {0,2}, {-1,2}}    // 3->0
};
```

### Scoring System

Standard Tetris scoring with level multiplier:

```c
int CalculateScore(int lines_cleared, int level) {
    int base_score = 0;
    switch(lines_cleared) {
        case 1: base_score = 100; break;   // Single
        case 2: base_score = 300; break;   // Double
        case 3: base_score = 500; break;   // Triple
        case 4: base_score = 800; break;   // Quadtris!
    }
    return base_score * level;
}
```

### Drop Speed Formula

Exponential increase in difficulty:

```c
float GetDropSpeed(int level) {
    return pow(0.8 - ((level - 1) * 0.007), level - 1);
}
```

### 7-Bag Randomizer

Ensures fair distribution of pieces:

```c
int bag[7] = {0, 1, 2, 3, 4, 5, 6};
int bag_index = 7;

int GetNextPiece() {
    if (bag_index >= 7) {
        // Shuffle bag
        for (int i = 6; i > 0; i--) {
            int j = rand() % (i + 1);
            int temp = bag[i];
            bag[i] = bag[j];
            bag[j] = temp;
        }
        bag_index = 0;
    }
    return bag[bag_index++];
}
```

---

## Future Enhancements

- **Hold Piece**: Allow player to swap current piece with held piece
- **Ghost Piece**: Show where piece will land
- **T-Spin Detection**: Award bonus points for T-piece rotations into tight spaces
- **Combo System**: Consecutive line clears award multipliers
- **Hard Drop**: Instantly drop piece to bottom
- **Soft Drop**: Faster controlled drop with points bonus
- **Marathon Mode**: Play until game over
- **Sprint Mode**: Clear 40 lines as fast as possible
- **Ultra Mode**: Score as many points as possible in 3 minutes
