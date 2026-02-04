
# Procedures from Tables, Funcs, and Tests

Games which are Projects:

1. [Pong](pong.md) - See detailed implementation
2. [Snake](snake.md) - See detailed implementation
3. Quadtris
4. Breakout

Simulations are a series of Procedures that produce immutable Tables using Functions.

Each project has a yaml file in the `projects/` folder.

Each project has a list of Procedures in its yaml file.
Each project has an Setup and Loop event.

Each Proecedure has

- a name
- a list of tables it uses
- a list of functions it uses, called in sequence

A Table has:

- a name
- a list of columns
- each column has a name and a type

A Function has:

- a name
- one or more input tables
- one or more output tables
- an optional list of parameters
- a body of code that uses the input tables, parameters, and produces the output tables
- functions have for each loops and if statements
- functions can call other functions, but dont have to

---

Imagine the runtime has an Arduino style main loop:

```c
int main() {
  Setup();
  while (true) {
    Loop();
  }
}
```

---

Inspiration: The Elm Architecture, ECS, and Scratch Programming Language.
How can we make programming more visual and modular?

Functions are pure and have no side effects.
They return new Tables based on input Tables.

Imagine that we reassign the output Tables to the input Tables after each function call.
Double buffer style. We have to thread them through the functions somehow.
Maybe just as globals, lol? Maybe a single state struct that holds all the tables?

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
