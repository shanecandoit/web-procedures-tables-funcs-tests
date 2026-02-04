// Generated Code for Project: Snake
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// --- Configuration Constants ---
#define SCREEN_WIDTH 800.0f
#define SCREEN_HEIGHT 600.0f
#define SNAKE_SIZE 20.0f
#define SNAKE_SPEED 5.0f
#define SNACK_RADIUS 10.0f
#define INITIAL_BODY_LENGTH 3
#define GRID_SIZE 20.0f

// --- Table Structures ---
typedef struct {
    float x;
    float y;
    float directionX;
    float directionY;
    float size;
} SnakeheadTable;

typedef struct {
    int pos_x[100];
    int pos_y[100];
    int length;
} SnakebodyTable;

typedef struct {
    float x;
    float y;
    float radius;
    int active;
} SnacksTable;

typedef struct {
    int points;
    int highScore;
} ScoreTable;

typedef struct {
    float elapsed;
    int gameState;
} TimerTable;

// --- Global State (Double Buffering) ---
struct GameState {
    SnakeheadTable snake_head_curr;
    SnakeheadTable snake_head_next;
    SnakebodyTable snake_body_curr;
    SnakebodyTable snake_body_next;
    SnacksTable snacks_curr;
    SnacksTable snacks_next;
    ScoreTable score_curr;
    ScoreTable score_next;
    TimerTable timer_curr;
    TimerTable timer_next;
} state;

// --- Pure Logic Prototypes ---
SnakeheadTable Logic_InitSnakeHead();
SnakebodyTable Logic_InitSnakeBody();
SnacksTable Logic_InitSnacks();
ScoreTable Logic_InitScore();
TimerTable Logic_InitTimer();
TimerTable Logic_UpdateTimer(TimerTable timer_in);
SnakeheadTable Logic_ProcessInput(SnakeheadTable snake_head_in);
SnakeheadTable Logic_MoveSnakeHead(SnakeheadTable snake_head_in, TimerTable timer_in);
SnakebodyTable Logic_MoveSnakeBody(SnakeheadTable snake_head_in, SnakebodyTable snake_body_in, TimerTable timer_in);
void Logic_CheckSnackCollision(SnakeheadTable snake_head_in, SnakebodyTable snake_body_in, SnacksTable snacks_in, SnakebodyTable* snake_body_out, SnacksTable* snacks_out);
TimerTable Logic_CheckWallCollision(SnakeheadTable snake_head_in, TimerTable timer_in);
TimerTable Logic_CheckSelfCollision(SnakeheadTable snake_head_in, SnakebodyTable snake_body_in, TimerTable timer_in);
ScoreTable Logic_UpdateScore(ScoreTable score_in, SnacksTable snacks_in);
SnacksTable Logic_SpawnSnack(SnacksTable snacks_in, SnakebodyTable snake_body_in);

// --- Generated Wrappers ---
void Wrapper_InitSnakeHead() {
    state.snake_head_next = Logic_InitSnakeHead();
    state.snake_head_curr = state.snake_head_next;
}

void Wrapper_InitSnakeBody() {
    state.snake_body_next = Logic_InitSnakeBody();
    state.snake_body_curr = state.snake_body_next;
}

void Wrapper_InitSnacks() {
    state.snacks_next = Logic_InitSnacks();
    state.snacks_curr = state.snacks_next;
}

void Wrapper_InitScore() {
    state.score_next = Logic_InitScore();
    state.score_curr = state.score_next;
}

void Wrapper_InitTimer() {
    state.timer_next = Logic_InitTimer();
    state.timer_curr = state.timer_next;
}

void Wrapper_UpdateTimer() {
    state.timer_next = Logic_UpdateTimer(state.timer_curr);
}

void Wrapper_ProcessInput() {
    state.snake_head_next = Logic_ProcessInput(state.snake_head_curr);
}

void Wrapper_MoveSnakeHead() {
    state.snake_head_next = Logic_MoveSnakeHead(state.snake_head_curr, state.timer_curr);
}

void Wrapper_MoveSnakeBody() {
    state.snake_body_next = Logic_MoveSnakeBody(state.snake_head_curr, state.snake_body_curr, state.timer_curr);
}

void Wrapper_CheckSnackCollision() {
    Logic_CheckSnackCollision(state.snake_head_curr, state.snake_body_curr, state.snacks_curr, &state.snake_body_next, &state.snacks_next);
}

void Wrapper_CheckWallCollision() {
    state.timer_next = Logic_CheckWallCollision(state.snake_head_curr, state.timer_curr);
}

void Wrapper_CheckSelfCollision() {
    state.timer_next = Logic_CheckSelfCollision(state.snake_head_curr, state.snake_body_curr, state.timer_curr);
}

void Wrapper_UpdateScore() {
    state.score_next = Logic_UpdateScore(state.score_curr, state.snacks_curr);
}

void Wrapper_SpawnSnack() {
    state.snacks_next = Logic_SpawnSnack(state.snacks_curr, state.snake_body_curr);
}

// --- Buffer Swap ---
void Swap_Buffers() {
    state.snake_head_curr = state.snake_head_next;
    state.snake_body_curr = state.snake_body_next;
    state.snacks_curr = state.snacks_next;
    state.score_curr = state.score_next;
    state.timer_curr = state.timer_next;
}

// --- High Level Procedures ---
void Setup() {
    Wrapper_InitSnakeHead();
    Wrapper_InitSnakeBody();
    Wrapper_InitSnacks();
    Wrapper_InitScore();
    Wrapper_InitTimer();
}

void Loop() {
    Wrapper_UpdateTimer();
    Wrapper_ProcessInput();
    Wrapper_MoveSnakeHead();
    Wrapper_MoveSnakeBody();
    Wrapper_CheckSnackCollision();
    Wrapper_CheckWallCollision();
    Wrapper_CheckSelfCollision();
    Wrapper_UpdateScore();
    Wrapper_SpawnSnack();
    Swap_Buffers();
}

int main() {
    Setup();
    while (true) {
        Loop();
    }
    return 0;
}