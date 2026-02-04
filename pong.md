# Pong Implementation

## Overview

Pong is used as an example implementation of the Procedures, Tables, and Functions architecture.

## Data Structures

```c
void Setup();
void Loop();
struct Paddle { float x; float y; float width; float height; };
struct Ball { float x; float y; float radius; float speedX; float speedY; };
struct Score { int player1; int player2; };
Paddle paddle, paddle_next;
Ball ball, ball_next;
Score score, score_next;
int main() {
  Setup();
  while (true) {
    Loop();
  }
}
void Setup() {
  InitPaddle();
  InitBall();
  InitScore();
}
void Loop() {
  MovePaddle();
  MoveBall();
  CheckScore();
  GameLost();
  GameWon();
}
```

## Procedures

- **Setup**
  - Tables: Paddle, Ball, Score
  - Functions: InitPaddle, InitBall, InitScore
- **Loop**
  - Tables: Paddle, Ball, Score
  - Functions: MovePaddle, MoveBall, CheckScore, GameLost, GameWon
- **MoveBall**
  - Tables: Ball
- **CheckScore**
  - Tables: Score
- **InitPaddle**
  - Tables: Paddle
- **InitBall**
  - Tables: Ball
- **InitScore**
  - Tables: Score
- **MovePaddle**
  - Tables: Paddle
- **GameLost**
  - Tables: Score
- **GameWon**
  - Tables: Score

## Tables

- **Paddle**
  - Columns: x (number), y (number), width (number), height (number)
- **Ball**
  - Columns: x (number), y (number), radius (number), speedX (number), speedY (number)
- **Score**
  - Columns: player1 (number), player2 (number)

## Functions

- **InitPaddle**
  - Input Tables: none
  - Output Tables: Paddle
  - Body: sets initial position and size of paddle
- **InitBall**
  - Input Tables: none
  - Output Tables: Ball
  - Body: sets initial position, radius, and speed of ball
- **InitScore**
  - Input Tables: none
  - Output Tables: Score
  - Body: sets initial scores to 0

## Threading Tables Through Functions

To thread tables through functions while maintaining high-level modularity (drag-and-drop reordering), you must decouple the **Logic Definition** (the pure function) from the **Data Wiring** (the generated glue code).

The architecture relies on three distinct layers:

1. **The State Container:** Holds the canonical version of all Tables (Current and Next).
2. **The Pure Core:** Functions that calculate logic without knowing about the game loop.
3. **The Generated Wrappers:** The bridge that "threads" the global state into the pure core.

### 1. The State Container (Memory)

To enable reordering and double buffering, the data must exist outside the functions. Use a global structure in the generated C code that holds two copies of every table: `_curr` (Read-Only during loop) and `_next` (Write-Only during loop).

```c
// Generated: game_state.h
typedef struct {
    float x, y, width, height;
} Paddle_Table;

typedef struct {
    float x, y, radius, dx, dy;
} Ball_Table;

// Double buffering storage
struct GameState {
    Paddle_Table paddle_curr;
    Paddle_Table paddle_next;
    Ball_Table   ball_curr;
    Ball_Table   ball_next;
} state;
```

### 2. The Pure Core (User Logic)

These functions are strictly input/output. They do not know "state" exists. This mimics the Elm/Functional architecture. They are easier to test because they are isolated.

```c
// User defined or standard library
Paddle_Table Logic_MovePaddle(Paddle_Table p) {
    p.y = p.y + 1.0; // Simple logic
    return p;
}

// Function requiring multiple tables (e.g., collision)
// Returns the NEW ball state based on current ball + current paddle
Ball_Table Logic_BounceBall(Ball_Table b, Paddle_Table p) {
    if (CheckCollision(b, p)) {
        b.dx = -b.dx;
    }
    return b;
}
```

### 3. The Generated Wrappers (The Wiring)

This is where the "Threading" happens. Your code generator reads the YAML, sees that `MovePaddle` needs the `Paddle` table, and generates a `void` wrapper. This wrapper handles the `_next = func(_curr)` assignment.

The High-Level Drag-and-Drop blocks correspond to these **Wrappers**, not the logic functions.

```c
// Generated: wrappers.c

// Wrapper for MovePaddle
// Knows specifically to read paddle_curr and write to paddle_next
void Wrapper_MovePaddle() {
    state.paddle_next = Logic_MovePaddle(state.paddle_curr);
}

// Wrapper for BounceBall
// Knows to wire up both Ball and Paddle, but only updates Ball
void Wrapper_BounceBall() {
    state.ball_next = Logic_BounceBall(state.ball_curr, state.paddle_curr);
}

// The "Commit" phase - occurs at end of frame
void Swap_Buffers() {
    state.paddle_curr = state.paddle_next;
    state.ball_curr = state.ball_next;
}
```

### The Main Loop (The Visual Result)

Because the Wrappers handle the threading internally based on the code-gen analysis, the main loop remains clean and reorderable.

```c
void Loop() {
    // These can be dragged/dropped in any order.
    // Dependencies are resolved inside the wrapper.
    Wrapper_MovePaddle();
    Wrapper_BounceBall();
    Wrapper_CheckScore();

    // Finalize frame
    Swap_Buffers();
}
```

### Code Generation Logic

To implement this, your YAML parser needs to perform **Dependency Injection** at generation time.

**YAML Input:**

```yaml
Function: MovePaddle
  Read: [Paddle]
  Write: [Paddle]
Function: BounceBall
  Read: [Ball, Paddle]
  Write: [Ball]
```

**Generator Logic (Pseudocode):**

1. **Parse Function:** `BounceBall`
2. **Identify Reads:** `Ball`, `Paddle` -> generate args `state.ball_curr`, `state.paddle_curr`
3. **Identify Writes:** `Ball` -> generate assignment target `state.ball_next`
4. **Emit Wrapper:** `void Wrapper_BounceBall() { state.ball_next = Logic_BounceBall(...); }`

### Handling Execution Order Dependencies

If `MovePaddle` runs _before_ `BounceBall`, `BounceBall` will see the **old** paddle position (because it reads `_curr`).
If `MovePaddle` runs _after_ `BounceBall`, `BounceBall` still sees the **old** paddle position.

This is the strict nature of **Double Buffering**. All functions in a frame read the state as it was at the _start_ of the frame. This eliminates race conditions where reordering blocks accidentally breaks physics.

If you require `BounceBall` to see the _updated_ paddle position immediately (within the same frame), you must abandon strict double buffering for a **Pipeline** approach:

**Pipeline Alternative (Sequential Mutation):**

1. Wrapper reads `_curr`.
2. Wrapper writes `_curr` (destructively).
3. Next wrapper reads updated `_curr`.

**Recommendation:** Stick to strict Double Buffering for simulations/games. It is more robust. If immediate updates are needed, those logic steps should likely be inside a single Function (e.g., `UpdatePhysics` which handles both Move and Bounce), rather than separate blocks.

### Summary of Data Flow

1. **Input:** `InitPaddle()` (Writes initial state to `_curr` and `_next`).
2. **Step 1:** `Wrapper_MovePaddle` reads `Paddle_curr` -> runs logic -> writes `Paddle_next`.
3. **Step 2:** `Wrapper_MoveBall` reads `Ball_curr` -> runs logic -> writes `Ball_next`.
4. **Step 3:** `Swap_Buffers` copies all `_next` to `_curr`.

## Implementation Files

### pong.yaml

This file defines the data schema and the execution order.

```yaml
project_name: Pong

tables:
  paddle:
    columns:
      x: float
      y: float
      width: float
      height: float
  ball:
    columns:
      x: float
      y: float
      radius: float
      speedX: float
      speedY: float
  score:
    columns:
      p1: int
      p2: int

# Pure Logic definitions
# 'input' is read-only (current state)
# 'output' is write-only (next state)
functions:
  InitPaddle:
    inputs: []
    outputs: [paddle]
  InitBall:
    inputs: []
    outputs: [ball]
  InitScore:
    inputs: []
    outputs: [score]
  MovePaddle:
    inputs: [paddle]
    outputs: [paddle]
  MoveBall:
    inputs: [ball, paddle] # Ball logic needs paddle pos to bounce
    outputs: [ball]
  CheckScore:
    inputs: [ball, score]
    outputs: [score]

# High level ordering of logic blocks
procedures:
  Setup:
    - InitPaddle
    - InitBall
    - InitScore
  Loop:
    - MovePaddle
    - MoveBall
    - CheckScore
```

### codegen.py

This script parses the YAML and generates `game.c`. It creates the structs, the global state container (double buffered), and the wrapper functions that thread the tables.

```python
import yaml

def generate_c_code(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    code = []

    # --- 1. Header & Type Definitions ---
    code.append(f"// Generated Code for Project: {data['project_name']}")
    code.append("#include <stdbool.h>\n")

    # Generate Structs for Tables
    code.append("// --- Table Structures ---")
    for table_name, table_data in data['tables'].items():
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"typedef struct {{")
        for col_name, col_type in table_data['columns'].items():
            code.append(f"    {col_type} {col_name};")
        code.append(f"}} {struct_name};\n")

    # --- 2. Global State (Double Buffering) ---
    code.append("// --- Global State (Double Buffered) ---")
    code.append("struct GameState {")
    for table_name in data['tables']:
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"    {struct_name} {table_name}_curr;")
        code.append(f"    {struct_name} {table_name}_next;")
    code.append("} state;\n")

    # --- 3. Pure Logic Function Prototypes ---
    # These are the functions the user would write logic for
    code.append("// --- Pure Logic Prototypes (User Implemented) ---")
    for func_name, func_data in data['functions'].items():
        outputs = func_data.get('outputs', [])
        inputs = func_data.get('inputs', [])

        # Determine return type (void if multiple outputs, struct if single)
        # For simplicity in this example, we assume 1 output table maps to return type
        # If no output, void.

        if len(outputs) == 1:
            ret_type = f"{outputs[0].capitalize()}Table"
        else:
            ret_type = "void" # Complex case handled via pointers in real world

        params = []
        for inp in inputs:
             params.append(f"{inp.capitalize()}Table {inp}_in")

        param_str = ", ".join(params)
        code.append(f"{ret_type} Logic_{func_name}({param_str});")
    code.append("")

    # --- 4. Generated Wrappers (The Threading) ---
    code.append("// --- Generated Wrappers (The Wiring) ---")
    for func_name, func_data in data['functions'].items():
        inputs = func_data.get('inputs', [])
        outputs = func_data.get('outputs', [])

        code.append(f"void Wrapper_{func_name}() {{")

        # Build arguments from CURRENT state
        args = [f"state.{inp}_curr" for inp in inputs]
        args_str = ", ".join(args)

        # Generate call and assignment to NEXT state
        if len(outputs) == 1:
            out_table = outputs[0]
            code.append(f"    state.{out_table}_next = Logic_{func_name}({args_str});")

            # Special case: Init functions should populate 'curr' as well
            # so the first loop has data without a swap.
            if "Init" in func_name:
                 code.append(f"    state.{out_table}_curr = state.{out_table}_next;")

        code.append("}\n")

    # --- 5. Buffer Swap Logic ---
    code.append("// --- Buffer Swap ---")
    code.append("void Swap_Buffers() {")
    for table_name in data['tables']:
        code.append(f"    state.{table_name}_curr = state.{table_name}_next;")
    code.append("}\n")

    # --- 6. Procedures (Setup / Loop) ---
    code.append("// --- High Level Procedures ---")
    for proc_name, func_list in data['procedures'].items():
        code.append(f"void {proc_name}() {{")
        for func in func_list:
            code.append(f"    Wrapper_{func}();")

        # If it's the Loop, we swap at the end
        if proc_name == "Loop":
             code.append("    Swap_Buffers();")
        code.append("}\n")

    # --- 7. Main ---
    code.append("// --- Main Entry Point ---")
    code.append("int main() {")
    code.append("    Setup();")
    code.append("    while (true) {")
    code.append("        Loop();")
    code.append("    }")
    code.append("    return 0;")
    code.append("}")

    return "\n".join(code)

# Run generation
if __name__ == "__main__":
    generated_c = generate_c_code('pong.yaml')
    print(generated_c)
    # with open("game.c", "w") as f:
    #     f.write(generated_c)
```

### Generated C Code

This is what the Python script produces based on the YAML.

```c
// Generated Code for Project: Pong
#include <stdbool.h>

// --- Table Structures ---
typedef struct {
  float x;
  float y;
  float width;
  float height;
} PaddleTable;

typedef struct {
  float x;
  float y;
  float radius;
  float speedX;
  float speedY;
} BallTable;

typedef struct {
  int p1;
  int p2;
} ScoreTable;

// --- Global State (Double Buffered) ---
struct GameState {
  PaddleTable paddle_curr;
  PaddleTable paddle_next;
  BallTable ball_curr;
  BallTable ball_next;
  ScoreTable score_curr;
  ScoreTable score_next;
} state;

// --- Pure Logic Prototypes (User Implemented) ---
PaddleTable Logic_InitPaddle();
BallTable Logic_InitBall();
ScoreTable Logic_InitScore();
PaddleTable Logic_MovePaddle(PaddleTable paddle_in);
BallTable Logic_MoveBall(BallTable ball_in, PaddleTable paddle_in);
ScoreTable Logic_CheckScore(BallTable ball_in, ScoreTable score_in);

// --- Generated Wrappers (The Wiring) ---
void Wrapper_InitPaddle() {
  state.paddle_next = Logic_InitPaddle();
  state.paddle_curr = state.paddle_next;
}

void Wrapper_InitBall() {
  state.ball_next = Logic_InitBall();
  state.ball_curr = state.ball_next;
}

void Wrapper_InitScore() {
  state.score_next = Logic_InitScore();
  state.score_curr = state.score_next;
}

void Wrapper_MovePaddle() {
  state.paddle_next = Logic_MovePaddle(state.paddle_curr);
}

void Wrapper_MoveBall() {
  state.ball_next = Logic_MoveBall(state.ball_curr, state.paddle_curr);
}

void Wrapper_CheckScore() {
  state.score_next = Logic_CheckScore(state.ball_curr, state.score_curr);
}

// --- Buffer Swap ---
void Swap_Buffers() {
  state.paddle_curr = state.paddle_next;
  state.ball_curr = state.ball_next;
  state.score_curr = state.score_next;
}

// --- High Level Procedures ---
void Setup() {
  Wrapper_InitPaddle();
  Wrapper_InitBall();
  Wrapper_InitScore();
}

void Loop() {
  Wrapper_MovePaddle();
  Wrapper_MoveBall();
  Wrapper_CheckScore();
  Swap_Buffers();
}

// --- Main Entry Point ---
int main() {
  Setup();
  while (true) {
    Loop();
  }
  return 0;
}
```

## Logic Implementation

The following implementation adheres to the pure function requirement. Each function receives a snapshot of the current state and returns a new state. No global variables are modified within these functions.

```c
// pong_logic.c
#include "game.h" // Assumes the generated structs are in game.h

// --- Configuration Parameters ---
// Users can modify these values to change physics behavior.
#define SCREEN_WIDTH 800.0f
#define SCREEN_HEIGHT 600.0f

#define PADDLE_WIDTH 15.0f
#define PADDLE_HEIGHT 80.0f
#define PADDLE_SPEED 5.0f

#define BALL_RADIUS 8.0f
#define BALL_START_SPEED_X 4.0f
#define BALL_START_SPEED_Y 3.0f

// --- Initialization Logic ---

PaddleTable Logic_InitPaddle() {
  PaddleTable p;
  p.x = 30.0f; // Offset from left wall
  p.y = (SCREEN_HEIGHT / 2.0f) - (PADDLE_HEIGHT / 2.0f);
  p.width = PADDLE_WIDTH;
  p.height = PADDLE_HEIGHT;
  return p;
}

BallTable Logic_InitBall() {
  BallTable b;
  b.x = SCREEN_WIDTH / 2.0f;
  b.y = SCREEN_HEIGHT / 2.0f;
  b.radius = BALL_RADIUS;
  b.speedX = BALL_START_SPEED_X;
  b.speedY = BALL_START_SPEED_Y;
  return b;
}

ScoreTable Logic_InitScore() {
  ScoreTable s;
  s.p1 = 0;
  s.p2 = 0;
  return s;
}

// --- Frame Logic ---

PaddleTable Logic_MovePaddle(PaddleTable p_in) {
  PaddleTable p_out = p_in;

  // In a real system, 'input' would be a table passed in.
  // For this simulation logic, we assume a simple automated follow or static move.
  // Move paddle down if it hasn't hit the bottom.
  if (p_out.y + p_out.height < SCREEN_HEIGHT) {
    p_out.y += PADDLE_SPEED;
  } else {
    p_out.y = 0; // Wrap around for simulation visual feedback
  }

  return p_out;
}

BallTable Logic_MoveBall(BallTable b_in, PaddleTable p_in) {
  BallTable b_out = b_in;

  // Apply Velocity
  b_out.x += b_out.speedX;
  b_out.y += b_out.speedY;

  // Physics: Top and Bottom Wall Bounce
  if (b_out.y - b_out.radius <= 0 || b_out.y + b_out.radius >= SCREEN_HEIGHT) {
    b_out.speedY *= -1.0f; // Reverse vertical direction
  }

  // Physics: Paddle Collision
  // Simple AABB (Axis-Aligned Bounding Box) check
  bool hit_x = (b_out.x - b_out.radius <= p_in.x + p_in.width) &&
    (b_out.x + b_out.radius >= p_in.x);
  bool hit_y = (b_out.y >= p_in.y) &&
    (b_out.y <= p_in.y + p_in.height);

  if (hit_x && hit_y) {
    b_out.speedX *= -1.05f; // Reverse and slightly increase speed
    b_out.x = p_in.x + p_in.width + b_out.radius; // Resolve overlap
  }

  return b_out;
}

ScoreTable Logic_CheckScore(BallTable b_in, ScoreTable s_in) {
    ScoreTable s_out = s_in;

    // Goal detection
    // Player 2 scores if ball passes left boundary
    if (b_in.x + b_in.radius < 0) {
        s_out.p2 += 1;
    }

    // Player 1 scores if ball passes right boundary
    if (b_in.x - b_in.radius > SCREEN_WIDTH) {
        s_out.p1 += 1;
    }

    return s_out;
}
```

### Physics Mechanics Summary

- **Pure State Transfer**: `b_out = b_in` ensures we start with the current state and only apply changes to the next state.
- **Velocity Integration**: Position is updated by adding speed per frame.
- **Boundary Constraint**: Vertical bounce uses a simple sign flip on `speedY`.
- **Collision Resolution**: When the ball hits the paddle, the speed is inverted and a small multiplier (1.05) is applied to increase difficulty. The ball's position is snapped to the paddle edge to prevent "sticky" collisions where the ball triggers the collision logic multiple times in one frame.
- **Scoring**: The score table is only incremented if the ball table's position exceeds the horizontal screen bounds.

---

```c
// pong_draw.c
#include "game.h" // Access to state.paddle_curr, state.ball_curr, etc.
#include <stdio.h>

// --- Visual Configuration ---
// Modify these to change the look of the game
#define COLOR_BG_R 20
#define COLOR_BG_G 20
#define COLOR_BG_B 25

#define COLOR_PADDLE_R 255
#define COLOR_PADDLE_G 255
#define COLOR_PADDLE_B 255

#define COLOR_BALL_R 255
#define COLOR_BALL_G 100
#define COLOR_BALL_B 100

#define COLOR_TEXT_R 200
#define COLOR_TEXT_G 200
#define COLOR_TEXT_B 200

#define NET_WIDTH 4.0f
#define SCORE_FONT_SIZE 32

// --- Drawing Procedure ---
// This function uses the _curr tables to ensure visual consistency
// while the physics might be calculating the _next tables in parallel.

void Draw_Project_Pong() {
  // 1. Clear Screen / Background
  // Processing: background(COLOR_BG_R, COLOR_BG_G, COLOR_BG_B);
  // SDL2: SDL_SetRenderDrawColor(renderer, 20, 20, 25, 255); SDL_RenderClear(renderer);
  API_DrawBackground(COLOR_BG_R, COLOR_BG_G, COLOR_BG_B);

  // 2. Draw Center Net (Static Visual)
  // Vertical dashed line logic
  for (float i = 0; i < 600; i += 40) {
    API_DrawRect(398, i, NET_WIDTH, 20, 100, 100, 100);
  }

  // 3. Render Paddle
  // Accessing the 'current' snapshot of the paddle table
  API_DrawRect(
    state.paddle_curr.x,
    state.paddle_curr.y,
    state.paddle_curr.width,
    state.paddle_curr.height,
    COLOR_PADDLE_R, COLOR_PADDLE_G, COLOR_PADDLE_B
  );
  // SDL2: SDL_Rect r = {state.paddle_curr.x, ...}; SDL_RenderFillRect(renderer, &r);

  // 4. Render Ball
  API_DrawCircle(
    state.ball_curr.x,
    state.ball_curr.y,
    state.ball_curr.radius,
    COLOR_BALL_R, COLOR_BALL_G, COLOR_BALL_B
  );
  // SDL2: requires a custom loop or SDL_RenderDrawPoint in a circle algorithm

  // 5. Render Scores
  char score_str[32];
  sprintf(score_str, "%d   %d", state.score_curr.p1, state.score_curr.p2);
  API_DrawText(score_str, 350, 50, SCORE_FONT_SIZE, COLOR_TEXT_R, COLOR_TEXT_G, COLOR_TEXT_B);
  // SDL2: requires SDL_ttf; TTF_RenderText_Solid(...) then SDL_CreateTextureFromSurface(...)
}

/*
Mapping of API_ functions to underlying SDL2 logic:

void API_DrawRect(float x, float y, float w, float h, int r, int g, int b) {
  SDL_SetRenderDrawColor(global_renderer, r, g, b, 255);
  SDL_FRect rect = { x, y, w, h };
  SDL_RenderFillRectF(global_renderer, &rect);
}

void API_DrawBackground(int r, int g, int b) {
  SDL_SetRenderDrawColor(global_renderer, r, g, b, 255);
  SDL_RenderClear(global_renderer);
}
*/

```
