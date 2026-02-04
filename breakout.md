# Breakout Implementation

## Overview

Breakout is a classic arcade game implemented using the Procedures, Tables, and Functions architecture. The player controls a paddle to bounce a ball and break bricks, aiming to clear all bricks without letting the ball fall off the bottom of the screen.

---

## Game Mechanics

- **Paddle Control**: The player moves a paddle horizontally at the bottom of the screen
- **Ball Physics**: The ball bounces off walls, the paddle, and bricks with realistic physics
- **Brick Breaking**: Bricks disappear when hit by the ball, awarding points
- **Lives System**: Player has limited lives; loses a life when ball falls below paddle
- **Win Condition**: Clear all bricks to win the level
- **Power-ups**: Optional items that fall when certain bricks are broken

---

## Data Structures

```c
void Setup();
void Loop();

struct Paddle { 
    float x; 
    float y; 
    float width; 
    float height; 
    float speed; 
};

struct Ball { 
    float x; 
    float y; 
    float radius; 
    float speedX; 
    float speedY; 
    int active; 
};

struct Bricks { 
    int grid[10][8];     // brick state: 0=destroyed, 1=normal, 2=strong, 3=unbreakable
    int rows; 
    int cols; 
    float brick_width; 
    float brick_height; 
    int remaining; 
};

struct Score { 
    int points; 
    int lives; 
    int level; 
    int highScore; 
};

struct GameState { 
    int state;  // 0=menu, 1=playing, 2=paused, 3=game_over, 4=level_complete
    float elapsed; 
};

Paddle paddle, paddle_next;
Ball ball, ball_next;
Bricks bricks, bricks_next;
Score score, score_next;
GameState game_state, game_state_next;

int main() {
  Setup();
  while (true) {
    Loop();
  }
}

void Setup() {
  InitPaddle();
  InitBall();
  InitBricks();
  InitScore();
  InitGameState();
}

void Loop() {
  UpdateGameState();
  ProcessInput();
  MovePaddle();
  MoveBall();
  CheckPaddleCollision();
  CheckWallCollision();
  CheckBrickCollision();
  CheckBallLost();
  UpdateScore();
  CheckWinCondition();
}
```

---

## Tables

### Paddle
- **Columns**: 
  - x (float) - Current x position (center)
  - y (float) - Current y position (near bottom of screen)
  - width (float) - Paddle width
  - height (float) - Paddle height
  - speed (float) - Movement speed

### Ball
- **Columns**: 
  - x (float) - Current x position
  - y (float) - Current y position
  - radius (float) - Ball radius
  - speedX (float) - Horizontal velocity
  - speedY (float) - Vertical velocity
  - active (int) - Whether ball is in play (1) or attached to paddle (0)

### Bricks
- **Columns**: 
  - grid (2D array) - State of each brick position
  - rows (int) - Number of brick rows
  - cols (int) - Number of brick columns
  - brick_width (float) - Width of each brick
  - brick_height (float) - Height of each brick
  - remaining (int) - Number of bricks left to break

### Score
- **Columns**: 
  - points (int) - Current score
  - lives (int) - Remaining lives
  - level (int) - Current level number
  - highScore (int) - Best score achieved

### GameState
- **Columns**: 
  - state (int) - Current game state: 0=menu, 1=playing, 2=paused, 3=game_over, 4=level_complete
  - elapsed (float) - Time elapsed in current level

---

## Procedures

### Setup
- **Tables**: Paddle, Ball, Bricks, Score, GameState
- **Functions**: InitPaddle, InitBall, InitBricks, InitScore, InitGameState

### Loop
- **Tables**: Paddle, Ball, Bricks, Score, GameState
- **Functions**: UpdateGameState, ProcessInput, MovePaddle, MoveBall, CheckPaddleCollision, CheckWallCollision, CheckBrickCollision, CheckBallLost, UpdateScore, CheckWinCondition

### Individual Procedures

- **InitPaddle**
  - Tables: Paddle
  - Purpose: Position paddle at bottom center of screen
  
- **InitBall**
  - Tables: Ball
  - Purpose: Create ball attached to paddle, ready for launch
  
- **InitBricks**
  - Tables: Bricks
  - Purpose: Generate brick layout for current level
  
- **InitScore**
  - Tables: Score
  - Purpose: Set initial score, lives (3), and level (1)
  
- **InitGameState**
  - Tables: GameState
  - Purpose: Set state to menu, elapsed to 0
  
- **UpdateGameState**
  - Tables: GameState
  - Purpose: Update game timer and handle state transitions
  
- **ProcessInput**
  - Tables: Paddle, Ball
  - Purpose: Handle player input for paddle movement and ball launch
  
- **MovePaddle**
  - Tables: Paddle
  - Purpose: Update paddle position based on input, constrain to screen bounds
  
- **MoveBall**
  - Tables: Ball
  - Purpose: Update ball position based on velocity
  
- **CheckPaddleCollision**
  - Tables: Ball, Paddle
  - Purpose: Detect and resolve ball-paddle collisions, apply spin
  
- **CheckWallCollision**
  - Tables: Ball
  - Purpose: Bounce ball off top and side walls
  
- **CheckBrickCollision**
  - Tables: Ball, Bricks
  - Purpose: Detect ball-brick collisions, destroy/damage bricks, reflect ball
  
- **CheckBallLost**
  - Tables: Ball, Score, GameState
  - Purpose: Detect if ball fell off screen, reduce lives
  
- **UpdateScore**
  - Tables: Score, Bricks
  - Purpose: Award points for bricks destroyed
  
- **CheckWinCondition**
  - Tables: Bricks, GameState
  - Purpose: Check if all bricks cleared, advance to next level

---

## Functions

### Initialization Functions

#### InitPaddle
- **Input Tables**: none
- **Output Tables**: Paddle
- **Body**: Sets paddle at horizontal center near bottom, with default width and speed

#### InitBall
- **Input Tables**: none
- **Output Tables**: Ball
- **Body**: Creates ball at paddle position, inactive (attached to paddle)

#### InitBricks
- **Input Tables**: none
- **Output Tables**: Bricks
- **Body**: Generates level layout with brick pattern and counts

#### InitScore
- **Input Tables**: none
- **Output Tables**: Score
- **Body**: Sets points to 0, lives to 3, level to 1, loads high score

#### InitGameState
- **Input Tables**: none
- **Output Tables**: GameState
- **Body**: Sets state to 0 (menu), elapsed to 0.0

### Game Loop Functions

#### UpdateGameState
- **Input Tables**: GameState
- **Output Tables**: GameState
- **Body**: Increments elapsed time, handles state-specific logic

#### ProcessInput
- **Input Tables**: Paddle, Ball
- **Output Tables**: Paddle, Ball
- **Body**: Reads keyboard/mouse input for paddle movement and spacebar to launch ball

#### MovePaddle
- **Input Tables**: Paddle
- **Output Tables**: Paddle
- **Body**: Updates x position based on speed, clamps to screen boundaries

#### MoveBall
- **Input Tables**: Ball
- **Output Tables**: Ball
- **Body**: Applies velocity to position if ball is active

#### CheckPaddleCollision
- **Input Tables**: Ball, Paddle
- **Output Tables**: Ball
- **Body**: Uses AABB collision detection; reflects ball and applies angle based on hit location

#### CheckWallCollision
- **Input Tables**: Ball
- **Output Tables**: Ball
- **Body**: Bounces ball off left, right, and top walls

#### CheckBrickCollision
- **Input Tables**: Ball, Bricks
- **Output Tables**: Ball, Bricks
- **Body**: Checks ball against all bricks, handles hits by reflecting ball and updating brick state

#### CheckBallLost
- **Input Tables**: Ball, Score, GameState
- **Output Tables**: Ball, Score, GameState
- **Body**: If ball y-position exceeds bottom boundary, reduce lives, reset ball, or trigger game over

#### UpdateScore
- **Input Tables**: Score, Bricks
- **Output Tables**: Score
- **Body**: Awards points based on bricks destroyed and updates high score

#### CheckWinCondition
- **Input Tables**: Bricks, GameState
- **Output Tables**: GameState
- **Body**: If remaining bricks is 0, set state to level_complete

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
Paddle paddle_curr, paddle_next;
Ball ball_curr, ball_next;
Bricks bricks_curr, bricks_next;
Score score_curr, score_next;
GameState game_state_curr, game_state_next;
```

### 2. The Pure Core (User-Defined Logic)

Each function is written in its pure form, accepting input tables as parameters and returning output tables:

```c
Ball MoveBall_Pure(Ball ball) {
    Ball result = ball;
    result.x += result.speedX;
    result.y += result.speedY;
    return result;
}

Ball CheckWallCollision_Pure(Ball ball) {
    Ball result = ball;
    if (result.x - result.radius <= 0 || result.x + result.radius >= SCREEN_WIDTH) {
        result.speedX = -result.speedX;
    }
    if (result.y - result.radius <= 0) {
        result.speedY = -result.speedY;
    }
    return result;
}
```

### 3. The Generated Wrappers (Glue Code)

The code generator creates wrappers that read from `_curr` and write to `_next`:

```c
void MoveBall_Wrapper() {
    ball_next = MoveBall_Pure(ball_curr);
}

void CheckWallCollision_Wrapper() {
    ball_next = CheckWallCollision_Pure(ball_next);
}
```

### The Loop (Generated)

The main loop is generated based on the procedure definitions:

```c
void Loop() {
    // Read current state into local copies
    Paddle paddle = paddle_curr;
    Ball ball = ball_curr;
    Bricks bricks = bricks_curr;
    Score score = score_curr;
    GameState game_state = game_state_curr;
    
    // Execute functions in order
    UpdateGameState_Wrapper();
    ProcessInput_Wrapper();
    MovePaddle_Wrapper();
    MoveBall_Wrapper();
    CheckPaddleCollision_Wrapper();
    CheckWallCollision_Wrapper();
    CheckBrickCollision_Wrapper();
    CheckBallLost_Wrapper();
    UpdateScore_Wrapper();
    CheckWinCondition_Wrapper();
    
    // Commit next state to current
    paddle_curr = paddle_next;
    ball_curr = ball_next;
    bricks_curr = bricks_next;
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

### Collision Detection Optimization

For brick collision, use spatial partitioning to avoid checking all bricks:

```c
// Calculate which grid cell the ball is in
int col = (int)(ball.x / bricks.brick_width);
int row = (int)(ball.y / bricks.brick_height);

// Only check nearby bricks (3x3 grid around ball)
for (int r = max(0, row-1); r <= min(bricks.rows-1, row+1); r++) {
    for (int c = max(0, col-1); c <= min(bricks.cols-1, col+1); c++) {
        // Check collision with brick at [r][c]
    }
}
```

### Paddle Collision Spin

Apply different reflection angles based on where ball hits paddle:

```c
float hitPosition = (ball.x - paddle.x) / (paddle.width / 2.0);  // -1 to 1
float angle = hitPosition * MAX_BOUNCE_ANGLE;  // e.g., 60 degrees
ball.speedX = ball_speed * sin(angle);
ball.speedY = -ball_speed * cos(angle);  // Always upward
```

### Brick Point Values

Different brick types can award different points:

```c
int GetBrickPoints(int brick_type) {
    switch(brick_type) {
        case 1: return 10;   // Normal brick
        case 2: return 20;   // Strong brick (requires 2 hits)
        case 3: return 0;    // Unbreakable
        default: return 0;
    }
}
```

---

## Future Enhancements

- **Power-ups**: Multi-ball, wider paddle, slower ball, sticky paddle
- **Multiple Levels**: Different brick patterns and difficulty
- **Visual Effects**: Particle effects for brick destruction
- **Sound**: Collision sounds and background music
- **Combo System**: Bonus points for consecutive hits
