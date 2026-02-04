# Snake Implementation

## Overview

Snake is a classic game implemented using the Procedures, Tables, and Functions architecture. The player controls a snake that grows longer as it eats snacks, with the goal of achieving the highest score without colliding with walls or itself.

---

## Game Mechanics

- **Snake Movement**: The snake head moves in a direction (up, down, left, right) and the body segments follow
- **Growth**: When the snake eats a snack, it grows by one segment
- **Collision Detection**: Game ends if the snake hits a wall or its own body
- **Scoring**: Points are awarded for each snack eaten
- **Snack Spawning**: New snacks appear at random locations

---

## Data Structures

```c
void Setup();
void Loop();

struct SnakeHead { 
    float x; 
    float y; 
    float directionX; 
    float directionY; 
    float size; 
};

struct SnakeBody { 
    int pos_x[100];  // x coordinates of each segment
    int pos_y[100];  // y coordinates of each segment
    int length; 
};

struct Snacks { 
    float x; 
    float y; 
    float radius; 
    int active; 
};

struct Score { 
    int points; 
    int highScore; 
};

struct Timer { 
    float elapsed; 
    int gameState;  // 0=playing, 1=paused, 2=game_over
};

SnakeHead snake_head, snake_head_next;
SnakeBody snake_body, snake_body_next;
Snacks snacks, snacks_next;
Score score, score_next;
Timer timer, timer_next;

int main() {
  Setup();
  while (true) {
    Loop();
  }
}

void Setup() {
  InitSnakeHead();
  InitSnakeBody();
  InitSnacks();
  InitScore();
  InitTimer();
}

void Loop() {
  UpdateTimer();
  ProcessInput();
  MoveSnakeHead();
  MoveSnakeBody();
  CheckSnackCollision();
  CheckWallCollision();
  CheckSelfCollision();
  UpdateScore();
  SpawnSnack();
}
```

---

## Tables

### SnakeHead
- **Columns**: 
  - x (float) - Current x position
  - y (float) - Current y position
  - directionX (float) - X component of movement direction (-1, 0, or 1)
  - directionY (float) - Y component of movement direction (-1, 0, or 1)
  - size (float) - Size of the snake head segment

### SnakeBody
- **Columns**: 
  - pos_x (array) - X coordinates of each body segment
  - pos_y (array) - Y coordinates of each body segment
  - length (int) - Current number of body segments

### Snacks
- **Columns**: 
  - x (float) - X position of the snack
  - y (float) - Y position of the snack
  - radius (float) - Size of the snack
  - active (int) - Whether snack is currently active (1) or eaten (0)

### Score
- **Columns**: 
  - points (int) - Current game score
  - highScore (int) - Highest score achieved

### Timer
- **Columns**: 
  - elapsed (float) - Time elapsed in current game
  - gameState (int) - Current state: 0=playing, 1=paused, 2=game_over

---

## Procedures

### Setup
- **Tables**: SnakeHead, SnakeBody, Snacks, Score, Timer
- **Functions**: InitSnakeHead, InitSnakeBody, InitSnacks, InitScore, InitTimer

### Loop
- **Tables**: SnakeHead, SnakeBody, Snacks, Score, Timer
- **Functions**: UpdateTimer, ProcessInput, MoveSnakeHead, MoveSnakeBody, CheckSnackCollision, CheckWallCollision, CheckSelfCollision, UpdateScore, SpawnSnack

### Individual Procedures

- **InitSnakeHead**
  - Tables: SnakeHead
  - Purpose: Initialize snake head at center, facing right
  
- **InitSnakeBody**
  - Tables: SnakeBody
  - Purpose: Initialize empty body or with starting segments
  
- **InitSnacks**
  - Tables: Snacks
  - Purpose: Spawn initial snack at random location
  
- **InitScore**
  - Tables: Score
  - Purpose: Set initial score to 0
  
- **InitTimer**
  - Tables: Timer
  - Purpose: Set game state to playing, elapsed to 0
  
- **UpdateTimer**
  - Tables: Timer
  - Purpose: Increment elapsed time, check game state
  
- **ProcessInput**
  - Tables: SnakeHead
  - Purpose: Update direction based on player input
  
- **MoveSnakeHead**
  - Tables: SnakeHead
  - Purpose: Move head in current direction
  
- **MoveSnakeBody**
  - Tables: SnakeHead, SnakeBody
  - Purpose: Move body segments to follow the head
  
- **CheckSnackCollision**
  - Tables: SnakeHead, Snacks, SnakeBody
  - Purpose: Detect if head collides with snack, grow snake
  
- **CheckWallCollision**
  - Tables: SnakeHead, Timer
  - Purpose: Check if snake hit wall, end game
  
- **CheckSelfCollision**
  - Tables: SnakeHead, SnakeBody, Timer
  - Purpose: Check if snake hit itself, end game
  
- **UpdateScore**
  - Tables: Score, Snacks
  - Purpose: Award points when snack is eaten
  
- **SpawnSnack**
  - Tables: Snacks, SnakeBody
  - Purpose: Generate new snack at valid location

---

## Functions

### Initialization Functions

#### InitSnakeHead
- **Input Tables**: none
- **Output Tables**: SnakeHead
- **Body**: Sets initial position at screen center, direction facing right, default size

#### InitSnakeBody
- **Input Tables**: none
- **Output Tables**: SnakeBody
- **Body**: Initializes with 3 starting segments behind the head

#### InitSnacks
- **Input Tables**: none
- **Output Tables**: Snacks
- **Body**: Spawns first snack at random position

#### InitScore
- **Input Tables**: none
- **Output Tables**: Score
- **Body**: Sets points to 0, loads high score from storage

#### InitTimer
- **Input Tables**: none
- **Output Tables**: Timer
- **Body**: Sets elapsed to 0.0, gameState to 0 (playing)

### Game Loop Functions

#### UpdateTimer
- **Input Tables**: Timer
- **Output Tables**: Timer
- **Body**: Increments elapsed time, maintains game state

#### ProcessInput
- **Input Tables**: SnakeHead
- **Output Tables**: SnakeHead
- **Body**: Reads keyboard input and updates direction (prevents 180-degree turns)

#### MoveSnakeHead
- **Input Tables**: SnakeHead
- **Output Tables**: SnakeHead
- **Body**: Updates position based on direction and speed

#### MoveSnakeBody
- **Input Tables**: SnakeHead, SnakeBody
- **Output Tables**: SnakeBody
- **Body**: Each segment moves to the position of the segment in front of it

---

## Threading Tables Through Functions

The Snake game uses the same double-buffering architecture as Pong. Each table has a `_curr` and `_next` version to ensure all functions read from a consistent state and write to the next state.

### State Container

```c
// Generated: game_state.h
typedef struct {
    float x, y, directionX, directionY, size;
} SnakeHead_Table;

typedef struct {
    int pos_x[100];
    int pos_y[100];
    int length;
} SnakeBody_Table;

typedef struct {
    float x, y, radius;
    int active;
} Snacks_Table;

typedef struct {
    int points, highScore;
} Score_Table;

typedef struct {
    float elapsed;
    int gameState;
} Timer_Table;

// Double buffering storage
struct GameState {
    SnakeHead_Table snake_head_curr;
    SnakeHead_Table snake_head_next;
    SnakeBody_Table snake_body_curr;
    SnakeBody_Table snake_body_next;
    Snacks_Table snacks_curr;
    Snacks_Table snacks_next;
    Score_Table score_curr;
    Score_Table score_next;
    Timer_Table timer_curr;
    Timer_Table timer_next;
} state;
```

### Pure Core Functions

These functions are strictly input/output with no side effects:

```c
// Movement logic
SnakeHead_Table Logic_MoveSnakeHead(SnakeHead_Table head) {
    head.x += head.directionX * SNAKE_SPEED;
    head.y += head.directionY * SNAKE_SPEED;
    return head;
}

// Body follows head
SnakeBody_Table Logic_MoveSnakeBody(SnakeBody_Table body, SnakeHead_Table head) {
    // Shift all segments forward
    for (int i = body.length - 1; i > 0; i--) {
        body.pos_x[i] = body.pos_x[i-1];
        body.pos_y[i] = body.pos_y[i-1];
    }
    // First segment follows head
    if (body.length > 0) {
        body.pos_x[0] = (int)head.x;
        body.pos_y[0] = (int)head.y;
    }
    return body;
}

// Collision detection
typedef struct {
    SnakeBody_Table body;
    Snacks_Table snacks;
} CollisionResult;

CollisionResult Logic_CheckSnackCollision(SnakeHead_Table head, SnakeBody_Table body, Snacks_Table snacks) {
    CollisionResult result;
    result.body = body;
    result.snacks = snacks;
    
    if (snacks.active) {
        float dx = head.x - snacks.x;
        float dy = head.y - snacks.y;
        float distance = sqrt(dx*dx + dy*dy);
        
        if (distance < head.size + snacks.radius) {
            // Snack eaten - grow snake and deactivate snack
            result.body.length++;
            result.snacks.active = 0;
        }
    }
    
    return result;
}
```

### Generated Wrappers

The wrappers handle the threading of global state:

```c
// Wrapper for MoveSnakeHead
void Wrapper_MoveSnakeHead() {
    state.snake_head_next = Logic_MoveSnakeHead(state.snake_head_curr);
}

// Wrapper for MoveSnakeBody
void Wrapper_MoveSnakeBody() {
    state.snake_body_next = Logic_MoveSnakeBody(
        state.snake_body_curr, 
        state.snake_head_curr
    );
}

// Wrapper for collision detection (multiple outputs)
void Wrapper_CheckSnackCollision() {
    CollisionResult result = Logic_CheckSnackCollision(
        state.snake_head_curr,
        state.snake_body_curr,
        state.snacks_curr
    );
    state.snake_body_next = result.body;
    state.snacks_next = result.snacks;
}

// Buffer swap at end of frame
void Swap_Buffers() {
    state.snake_head_curr = state.snake_head_next;
    state.snake_body_curr = state.snake_body_next;
    state.snacks_curr = state.snacks_next;
    state.score_curr = state.score_next;
    state.timer_curr = state.timer_next;
}
```

### Main Loop

```c
void Loop() {
    // All wrappers can be reordered via drag-and-drop
    Wrapper_UpdateTimer();
    Wrapper_ProcessInput();
    Wrapper_MoveSnakeHead();
    Wrapper_MoveSnakeBody();
    Wrapper_CheckSnackCollision();
    Wrapper_CheckWallCollision();
    Wrapper_CheckSelfCollision();
    Wrapper_UpdateScore();
    Wrapper_SpawnSnack();
    
    // Commit all changes
    Swap_Buffers();
}
```

---

## YAML Definition

### snake.yaml

```yaml
project_name: Snake

tables:
  snake_head:
    columns:
      x: float
      y: float
      directionX: float
      directionY: float
      size: float
  snake_body:
    columns:
      pos_x: array  # x coordinates of segments
      pos_y: array  # y coordinates of segments
      length: int
  snacks:
    columns:
      x: float
      y: float
      radius: float
      active: int
  score:
    columns:
      points: int
      highScore: int
  timer:
    columns:
      elapsed: float
      gameState: int

functions:
  InitSnakeHead:
    inputs: []
    outputs: [snake_head]
  InitSnakeBody:
    inputs: []
    outputs: [snake_body]
  InitSnacks:
    inputs: []
    outputs: [snacks]
  InitScore:
    inputs: []
    outputs: [score]
  InitTimer:
    inputs: []
    outputs: [timer]
  UpdateTimer:
    inputs: [timer]
    outputs: [timer]
  ProcessInput:
    inputs: [snake_head]
    outputs: [snake_head]
  MoveSnakeHead:
    inputs: [snake_head]
    outputs: [snake_head]
  MoveSnakeBody:
    inputs: [snake_head, snake_body]
    outputs: [snake_body]
  CheckSnackCollision:
    inputs: [snake_head, snake_body, snacks]
    outputs: [snake_body, snacks]
  CheckWallCollision:
    inputs: [snake_head, timer]
    outputs: [timer]
  CheckSelfCollision:
    inputs: [snake_head, snake_body, timer]
    outputs: [timer]
  UpdateScore:
    inputs: [score, snacks]
    outputs: [score]
  SpawnSnack:
    inputs: [snacks, snake_body]
    outputs: [snacks]

procedures:
  Setup:
    - InitSnakeHead
    - InitSnakeBody
    - InitSnacks
    - InitScore
    - InitTimer
  Loop:
    - UpdateTimer
    - ProcessInput
    - MoveSnakeHead
    - MoveSnakeBody
    - CheckSnackCollision
    - CheckWallCollision
    - CheckSelfCollision
    - UpdateScore
    - SpawnSnack
```

---

## Code Generation

The same `codegen.py` script from Pong can be used to generate the Snake game code. Simply run:

```bash
python codegen.py snake.yaml
```

This will generate the complete C code with:
- Table struct definitions
- Global state with double buffering
- Pure logic function prototypes
- Generated wrapper functions
- Buffer swap logic
- Setup and Loop procedures
- Main entry point

---

## Logic Implementation

### Configuration Constants

```c
// snake_logic.c
#include "game.h"

#define SCREEN_WIDTH 800.0f
#define SCREEN_HEIGHT 600.0f
#define GRID_SIZE 20.0f

#define SNAKE_SPEED 20.0f  // pixels per frame
#define SNAKE_SIZE 10.0f
#define SNACK_RADIUS 8.0f
#define INITIAL_LENGTH 3

#define GAME_PLAYING 0
#define GAME_PAUSED 1
#define GAME_OVER 2
```

### Initialization Logic

```c
SnakeHead_Table Logic_InitSnakeHead() {
    SnakeHead_Table h;
    h.x = SCREEN_WIDTH / 2.0f;
    h.y = SCREEN_HEIGHT / 2.0f;
    h.directionX = 1.0f;  // Start moving right
    h.directionY = 0.0f;
    h.size = SNAKE_SIZE;
    return h;
}

SnakeBody_Table Logic_InitSnakeBody() {
    SnakeBody_Table b;
    b.length = INITIAL_LENGTH;
    
    // Initialize segments behind the head
    float startX = SCREEN_WIDTH / 2.0f;
    float startY = SCREEN_HEIGHT / 2.0f;
    
    for (int i = 0; i < INITIAL_LENGTH; i++) {
        b.pos_x[i] = (int)(startX - (i + 1) * GRID_SIZE);
        b.pos_y[i] = (int)startY;
    }
    
    return b;
}

Snacks_Table Logic_InitSnacks() {
    Snacks_Table s;
    s.x = (float)(rand() % (int)(SCREEN_WIDTH - 40) + 20);
    s.y = (float)(rand() % (int)(SCREEN_HEIGHT - 40) + 20);
    s.radius = SNACK_RADIUS;
    s.active = 1;
    return s;
}

Score_Table Logic_InitScore() {
    Score_Table s;
    s.points = 0;
    s.highScore = 0;  // TODO: Load from storage
    return s;
}

Timer_Table Logic_InitTimer() {
    Timer_Table t;
    t.elapsed = 0.0f;
    t.gameState = GAME_PLAYING;
    return t;
}
```

### Movement Logic

```c
SnakeHead_Table Logic_MoveSnakeHead(SnakeHead_Table head_in) {
    SnakeHead_Table head_out = head_in;
    
    head_out.x += head_out.directionX * SNAKE_SPEED;
    head_out.y += head_out.directionY * SNAKE_SPEED;
    
    return head_out;
}

SnakeBody_Table Logic_MoveSnakeBody(SnakeHead_Table head_in, SnakeBody_Table body_in) {
    SnakeBody_Table body_out = body_in;
    
    // Shift all segments - each follows the one in front
    for (int i = body_out.length - 1; i > 0; i--) {
        body_out.pos_x[i] = body_out.pos_x[i-1];
        body_out.pos_y[i] = body_out.pos_y[i-1];
    }
    
    // First body segment follows the head
    if (body_out.length > 0) {
        body_out.pos_x[0] = (int)head_in.x;
        body_out.pos_y[0] = (int)head_in.y;
    }
    
    return body_out;
}
```

### Collision Detection

```c
typedef struct {
    SnakeBody_Table body;
    Snacks_Table snacks;
} SnackCollisionResult;

SnackCollisionResult Logic_CheckSnackCollision(
    SnakeHead_Table head_in, 
    SnakeBody_Table body_in, 
    Snacks_Table snacks_in
) {
    SnackCollisionResult result;
    result.body = body_in;
    result.snacks = snacks_in;
    
    if (result.snacks.active) {
        float dx = head_in.x - snacks_in.x;
        float dy = head_in.y - snacks_in.y;
        float distance = sqrt(dx * dx + dy * dy);
        
        if (distance < head_in.size + snacks_in.radius) {
            // Snack eaten!
            result.body.length++;
            result.snacks.active = 0;  // Mark for respawn
        }
    }
    
    return result;
}

Timer_Table Logic_CheckWallCollision(SnakeHead_Table head_in, Timer_Table timer_in) {
    Timer_Table timer_out = timer_in;
    
    if (head_in.x < 0 || head_in.x > SCREEN_WIDTH ||
        head_in.y < 0 || head_in.y > SCREEN_HEIGHT) {
        timer_out.gameState = GAME_OVER;
    }
    
    return timer_out;
}

Timer_Table Logic_CheckSelfCollision(
    SnakeHead_Table head_in, 
    SnakeBody_Table body_in, 
    Timer_Table timer_in
) {
    Timer_Table timer_out = timer_in;
    
    // Check if head collides with any body segment
    for (int i = 0; i < body_in.length; i++) {
        int segX = body_in.pos_x[i];
        int segY = body_in.pos_y[i];
        
        float dx = head_in.x - segX;
        float dy = head_in.y - segY;
        float distance = sqrt(dx * dx + dy * dy);
        
        if (distance < head_in.size) {
            timer_out.gameState = GAME_OVER;
            break;
        }
    }
    
    return timer_out;
}
```

### Scoring and Spawning

```c
Score_Table Logic_UpdateScore(Score_Table score_in, Snacks_Table snacks_in) {
    Score_Table score_out = score_in;
    
    // Award points if snack was just eaten (became inactive this frame)
    if (!snacks_in.active) {
        score_out.points += 10;
        
        if (score_out.points > score_out.highScore) {
            score_out.highScore = score_out.points;
        }
    }
    
    return score_out;
}

Snacks_Table Logic_SpawnSnack(Snacks_Table snacks_in, SnakeBody_Table body_in) {
    Snacks_Table snacks_out = snacks_in;
    
    // Only spawn if current snack is inactive
    if (!snacks_out.active) {
        // Find a position not occupied by snake body
        int validPosition = 0;
        int attempts = 0;
        
        while (!validPosition && attempts < 100) {
            snacks_out.x = (float)(rand() % (int)(SCREEN_WIDTH - 40) + 20);
            snacks_out.y = (float)(rand() % (int)(SCREEN_HEIGHT - 40) + 20);
            
            validPosition = 1;
            
            // Check against all body segments
            for (int i = 0; i < body_in.length; i++) {
                float dx = snacks_out.x - body_in.pos_x[i];
                float dy = snacks_out.y - body_in.pos_y[i];
                float distance = sqrt(dx * dx + dy * dy);
                
                if (distance < GRID_SIZE) {
                    validPosition = 0;
                    break;
                }
            }
            
            attempts++;
        }
        
        snacks_out.active = 1;
    }
    
    return snacks_out;
}
```

---

## Game Features Summary

### Core Mechanics
- **Grid-based movement**: Snake moves in discrete steps
- **Body following**: Each segment follows the previous one
- **Growth system**: Snake grows when eating snacks
- **Collision detection**: Wall and self-collision end the game

### State Management
- **Double buffering**: Ensures consistent state across all functions
- **Pure functions**: All game logic is deterministic and testable
- **Modular procedures**: Easy to reorder or modify game logic

### Extensibility
The architecture makes it easy to add:
- Different snack types with special effects
- Power-ups and obstacles
- Multiple difficulty levels
- Multiplayer support
- Different movement modes (smooth vs grid-based)
