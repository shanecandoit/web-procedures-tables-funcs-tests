// Generated Code for Project: Quadtris
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// --- Configuration Constants ---
#define SCREEN_WIDTH 400.0f
#define SCREEN_HEIGHT 800.0f
#define GRID_WIDTH 10
#define GRID_HEIGHT 20
#define CELL_SIZE 30.0f
#define INITIAL_DROP_SPEED 1.0f
#define LOCK_DELAY 0.5f
#define INITIAL_LIVES 3
#define LINES_PER_LEVEL 10
#define PREVIEW_COUNT 3

// --- Table Structures ---
typedef struct {
    int type;
    int rotation;
    float x;
    float y;
    int grid_x;
    int grid_y;
    int locked;
} ActivepieceTable;

typedef struct {
    int cells[100];
    int width;
    int height;
} GridTable;

typedef struct {
    int queue[100];
    int count;
} NextpiecesTable;

typedef struct {
    int points;
    int lines;
    int level;
    int highScore;
} ScoreTable;

typedef struct {
    int state;
    float dropTimer;
    float dropSpeed;
    float lockTimer;
    int canHold;
    int heldPiece;
} GamestateTable;

// --- Global State (Double Buffering) ---
struct GameState {
    ActivepieceTable active_piece_curr;
    ActivepieceTable active_piece_next;
    GridTable grid_curr;
    GridTable grid_next;
    NextpiecesTable next_pieces_curr;
    NextpiecesTable next_pieces_next;
    ScoreTable score_curr;
    ScoreTable score_next;
    GamestateTable game_state_curr;
    GamestateTable game_state_next;
} state;

// --- Pure Logic Prototypes ---
ActivepieceTable Logic_InitActivePiece();
GridTable Logic_InitGrid();
NextpiecesTable Logic_InitNextPieces();
ScoreTable Logic_InitScore();
GamestateTable Logic_InitGameState();
GamestateTable Logic_UpdateGameState(GamestateTable game_state_in);
void Logic_ProcessInput(ActivepieceTable active_piece_in, GamestateTable game_state_in, ActivepieceTable* active_piece_out, GamestateTable* game_state_out);
GamestateTable Logic_UpdateDropTimer(GamestateTable game_state_in);
void Logic_MoveActivePiece(ActivepieceTable active_piece_in, GamestateTable game_state_in, ActivepieceTable* active_piece_out, GamestateTable* game_state_out);
ActivepieceTable Logic_RotateActivePiece(ActivepieceTable active_piece_in);
ActivepieceTable Logic_CheckCollision(ActivepieceTable active_piece_in, GridTable grid_in);
void Logic_LockPiece(ActivepieceTable active_piece_in, GridTable grid_in, GamestateTable game_state_in, GridTable* grid_out, GamestateTable* game_state_out, ActivepieceTable* active_piece_out);
void Logic_ClearLines(GridTable grid_in, ScoreTable score_in, GridTable* grid_out, ScoreTable* score_out);
void Logic_SpawnNewPiece(ActivepieceTable active_piece_in, NextpiecesTable next_pieces_in, GamestateTable game_state_in, ActivepieceTable* active_piece_out, NextpiecesTable* next_pieces_out, GamestateTable* game_state_out);
void Logic_UpdateScore(ScoreTable score_in, GamestateTable game_state_in, ScoreTable* score_out, GamestateTable* game_state_out);
GamestateTable Logic_CheckGameOver(GridTable grid_in, ActivepieceTable active_piece_in, GamestateTable game_state_in);

// --- Generated Wrappers ---
void Wrapper_InitActivePiece() {
    state.active_piece_next = Logic_InitActivePiece();
    state.active_piece_curr = state.active_piece_next;
}

void Wrapper_InitGrid() {
    state.grid_next = Logic_InitGrid();
    state.grid_curr = state.grid_next;
}

void Wrapper_InitNextPieces() {
    state.next_pieces_next = Logic_InitNextPieces();
    state.next_pieces_curr = state.next_pieces_next;
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
    Logic_ProcessInput(state.active_piece_curr, state.game_state_curr, &state.active_piece_next, &state.game_state_next);
}

void Wrapper_UpdateDropTimer() {
    state.game_state_next = Logic_UpdateDropTimer(state.game_state_curr);
}

void Wrapper_MoveActivePiece() {
    Logic_MoveActivePiece(state.active_piece_curr, state.game_state_curr, &state.active_piece_next, &state.game_state_next);
}

void Wrapper_RotateActivePiece() {
    state.active_piece_next = Logic_RotateActivePiece(state.active_piece_curr);
}

void Wrapper_CheckCollision() {
    state.active_piece_next = Logic_CheckCollision(state.active_piece_curr, state.grid_curr);
}

void Wrapper_LockPiece() {
    Logic_LockPiece(state.active_piece_curr, state.grid_curr, state.game_state_curr, &state.grid_next, &state.game_state_next, &state.active_piece_next);
}

void Wrapper_ClearLines() {
    Logic_ClearLines(state.grid_curr, state.score_curr, &state.grid_next, &state.score_next);
}

void Wrapper_SpawnNewPiece() {
    Logic_SpawnNewPiece(state.active_piece_curr, state.next_pieces_curr, state.game_state_curr, &state.active_piece_next, &state.next_pieces_next, &state.game_state_next);
}

void Wrapper_UpdateScore() {
    Logic_UpdateScore(state.score_curr, state.game_state_curr, &state.score_next, &state.game_state_next);
}

void Wrapper_CheckGameOver() {
    state.game_state_next = Logic_CheckGameOver(state.grid_curr, state.active_piece_curr, state.game_state_curr);
}

// --- Buffer Swap ---
void Swap_Buffers() {
    state.active_piece_curr = state.active_piece_next;
    state.grid_curr = state.grid_next;
    state.next_pieces_curr = state.next_pieces_next;
    state.score_curr = state.score_next;
    state.game_state_curr = state.game_state_next;
}

// --- High Level Procedures ---
void Setup() {
    Wrapper_InitActivePiece();
    Wrapper_InitGrid();
    Wrapper_InitNextPieces();
    Wrapper_InitScore();
    Wrapper_InitGameState();
}

void Loop() {
    Wrapper_UpdateGameState();
    Wrapper_ProcessInput();
    Wrapper_UpdateDropTimer();
    Wrapper_MoveActivePiece();
    Wrapper_RotateActivePiece();
    Wrapper_CheckCollision();
    Wrapper_LockPiece();
    Wrapper_ClearLines();
    Wrapper_SpawnNewPiece();
    Wrapper_UpdateScore();
    Wrapper_CheckGameOver();
    Swap_Buffers();
}

int main() {
    Setup();
    while (true) {
        Loop();
    }
    return 0;
}