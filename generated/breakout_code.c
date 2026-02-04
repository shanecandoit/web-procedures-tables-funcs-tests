// Generated Code for Project: Breakout
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// --- Configuration Constants ---
#define SCREEN_WIDTH 800.0f
#define SCREEN_HEIGHT 600.0f
#define PADDLE_WIDTH 100.0f
#define PADDLE_HEIGHT 15.0f
#define PADDLE_SPEED 6.0f
#define BALL_RADIUS 8.0f
#define BALL_SPEED 5.0f
#define BRICK_ROWS 8
#define BRICK_COLS 10
#define BRICK_WIDTH 75.0f
#define BRICK_HEIGHT 20.0f
#define INITIAL_LIVES 3

// --- Table Structures ---
typedef struct {
    float x;
    float y;
    float width;
    float height;
    float speed;
} PaddleTable;

typedef struct {
    float x;
    float y;
    float radius;
    float speedX;
    float speedY;
    int active;
} BallTable;

typedef struct {
    int grid[100];
    int rows;
    int cols;
    float brick_width;
    float brick_height;
    int remaining;
} BricksTable;

typedef struct {
    int points;
    int lives;
    int level;
    int highScore;
} ScoreTable;

typedef struct {
    int state;
    float elapsed;
} GamestateTable;

// --- Global State (Double Buffering) ---
struct GameState {
    PaddleTable paddle_curr;
    PaddleTable paddle_next;
    BallTable ball_curr;
    BallTable ball_next;
    BricksTable bricks_curr;
    BricksTable bricks_next;
    ScoreTable score_curr;
    ScoreTable score_next;
    GamestateTable game_state_curr;
    GamestateTable game_state_next;
} state;

// --- Pure Logic Prototypes ---
PaddleTable Logic_InitPaddle();
BallTable Logic_InitBall();
BricksTable Logic_InitBricks();
ScoreTable Logic_InitScore();
GamestateTable Logic_InitGameState();
GamestateTable Logic_UpdateGameState(GamestateTable game_state_in);
void Logic_ProcessInput(PaddleTable paddle_in, BallTable ball_in, PaddleTable* paddle_out, BallTable* ball_out);
PaddleTable Logic_MovePaddle(PaddleTable paddle_in);
BallTable Logic_MoveBall(BallTable ball_in);
BallTable Logic_CheckPaddleCollision(BallTable ball_in, PaddleTable paddle_in);
BallTable Logic_CheckWallCollision(BallTable ball_in);
void Logic_CheckBrickCollision(BallTable ball_in, BricksTable bricks_in, BallTable* ball_out, BricksTable* bricks_out);
void Logic_CheckBallLost(BallTable ball_in, ScoreTable score_in, GamestateTable game_state_in, BallTable* ball_out, ScoreTable* score_out, GamestateTable* game_state_out);
ScoreTable Logic_UpdateScore(ScoreTable score_in, BricksTable bricks_in);
GamestateTable Logic_CheckWinCondition(BricksTable bricks_in, GamestateTable game_state_in);

// --- Generated Wrappers ---
void Wrapper_InitPaddle() {
    state.paddle_next = Logic_InitPaddle();
    state.paddle_curr = state.paddle_next;
}

void Wrapper_InitBall() {
    state.ball_next = Logic_InitBall();
    state.ball_curr = state.ball_next;
}

void Wrapper_InitBricks() {
    state.bricks_next = Logic_InitBricks();
    state.bricks_curr = state.bricks_next;
}

void Wrapper_InitScore() {
    state.score_next = Logic_InitScore();
    state.score_curr = state.score_next;
}

void Wrapper_InitGameState() {
    state.game_state_next = Logic_InitGameState();
    state.game_state_curr = state.game_state_next;
}

void Wrapper_UpdateGameState() {
    state.game_state_next = Logic_UpdateGameState(state.game_state_curr);
}

void Wrapper_ProcessInput() {
    Logic_ProcessInput(state.paddle_curr, state.ball_curr, &state.paddle_next, &state.ball_next);
}

void Wrapper_MovePaddle() {
    state.paddle_next = Logic_MovePaddle(state.paddle_curr);
}

void Wrapper_MoveBall() {
    state.ball_next = Logic_MoveBall(state.ball_curr);
}

void Wrapper_CheckPaddleCollision() {
    state.ball_next = Logic_CheckPaddleCollision(state.ball_curr, state.paddle_curr);
}

void Wrapper_CheckWallCollision() {
    state.ball_next = Logic_CheckWallCollision(state.ball_curr);
}

void Wrapper_CheckBrickCollision() {
    Logic_CheckBrickCollision(state.ball_curr, state.bricks_curr, &state.ball_next, &state.bricks_next);
}

void Wrapper_CheckBallLost() {
    Logic_CheckBallLost(state.ball_curr, state.score_curr, state.game_state_curr, &state.ball_next, &state.score_next, &state.game_state_next);
}

void Wrapper_UpdateScore() {
    state.score_next = Logic_UpdateScore(state.score_curr, state.bricks_curr);
}

void Wrapper_CheckWinCondition() {
    state.game_state_next = Logic_CheckWinCondition(state.bricks_curr, state.game_state_curr);
}

// --- Buffer Swap ---
void Swap_Buffers() {
    state.paddle_curr = state.paddle_next;
    state.ball_curr = state.ball_next;
    state.bricks_curr = state.bricks_next;
    state.score_curr = state.score_next;
    state.game_state_curr = state.game_state_next;
}

// --- High Level Procedures ---
void Setup() {
    Wrapper_InitPaddle();
    Wrapper_InitBall();
    Wrapper_InitBricks();
    Wrapper_InitScore();
    Wrapper_InitGameState();
}

void Loop() {
    Wrapper_UpdateGameState();
    Wrapper_ProcessInput();
    Wrapper_MovePaddle();
    Wrapper_MoveBall();
    Wrapper_CheckPaddleCollision();
    Wrapper_CheckWallCollision();
    Wrapper_CheckBrickCollision();
    Wrapper_CheckBallLost();
    Wrapper_UpdateScore();
    Wrapper_CheckWinCondition();
    Swap_Buffers();
}

int main() {
    Setup();
    while (true) {
        Loop();
    }
    return 0;
}