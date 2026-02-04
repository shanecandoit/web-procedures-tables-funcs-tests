// Generated Code for Project: Pong
#include <stdbool.h>
#include <stdio.h>

// --- Configuration Constants ---
#define SCREEN_WIDTH 800.0
#define SCREEN_HEIGHT 600.0
#define PADDLE_WIDTH 15.0
#define PADDLE_HEIGHT 80.0
#define PADDLE_SPEED 5.0
#define BALL_RADIUS 8.0
#define BALL_START_SPEED_X 4.0
#define BALL_START_SPEED_Y 3.0

// --- Table Structures ---
typedef struct {
    float x;
    float y;
    float width;
    float height;
} Paddle1Table;

typedef struct {
    float x;
    float y;
    float width;
    float height;
} Paddle2Table;

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

// --- Global State (Double Buffering) ---
struct GameState {
    Paddle1Table paddle1_curr;
    Paddle1Table paddle1_next;
    Paddle2Table paddle2_curr;
    Paddle2Table paddle2_next;
    BallTable ball_curr;
    BallTable ball_next;
    ScoreTable score_curr;
    ScoreTable score_next;
} state;

// --- Pure Logic Prototypes (User Implemented) ---
void Logic_InitPaddles(Paddle1Table* paddle1_out, Paddle2Table* paddle2_out);
BallTable Logic_InitBall();
ScoreTable Logic_InitScore();
Paddle1Table Logic_MovePaddle1(Paddle1Table paddle1_in);
Paddle2Table Logic_MovePaddle2(Paddle2Table paddle2_in, BallTable ball_in);
BallTable Logic_MoveBall(BallTable ball_in, Paddle1Table paddle1_in, Paddle2Table paddle2_in);
ScoreTable Logic_CheckScore(BallTable ball_in, ScoreTable score_in);
void Logic_GameLost(ScoreTable score_in);
void Logic_GameWon(ScoreTable score_in);

// --- Generated Wrappers (The Wiring) ---
void Wrapper_InitPaddles() {
    Logic_InitPaddles(&state.paddle1_next, &state.paddle2_next);
    state.paddle1_curr = state.paddle1_next;
    state.paddle2_curr = state.paddle2_next;
}

void Wrapper_InitBall() {
    state.ball_next = Logic_InitBall();
    state.ball_curr = state.ball_next;
}

void Wrapper_InitScore() {
    state.score_next = Logic_InitScore();
    state.score_curr = state.score_next;
}

void Wrapper_MovePaddle1() {
    state.paddle1_next = Logic_MovePaddle1(state.paddle1_curr);
}

void Wrapper_MovePaddle2() {
    state.paddle2_next = Logic_MovePaddle2(state.paddle2_curr, state.ball_curr);
}

void Wrapper_MoveBall() {
    state.ball_next = Logic_MoveBall(state.ball_curr, state.paddle1_curr, state.paddle2_curr);
}

void Wrapper_CheckScore() {
    state.score_next = Logic_CheckScore(state.ball_curr, state.score_curr);
}

void Wrapper_GameLost() {
    Logic_GameLost(state.score_curr);
}

void Wrapper_GameWon() {
    Logic_GameWon(state.score_curr);
}

// --- Buffer Swap ---
void Swap_Buffers() {
    state.paddle1_curr = state.paddle1_next;
    state.paddle2_curr = state.paddle2_next;
    state.ball_curr = state.ball_next;
    state.score_curr = state.score_next;
}

// --- High Level Procedures ---
void Setup() {
    Wrapper_InitPaddles();
    Wrapper_InitBall();
    Wrapper_InitScore();
}

void Loop() {
    Wrapper_MovePaddle1();
    Wrapper_MovePaddle2();
    Wrapper_MoveBall();
    Wrapper_CheckScore();
    Wrapper_GameLost();
    Wrapper_GameWon();
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