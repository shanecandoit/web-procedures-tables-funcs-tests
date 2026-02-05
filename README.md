# LogicCanvas: Visual Game Design with Procedures, Tables, and Functions

LogicCanvas is an experimental framework for designing and generating games using a declarative, data-driven architecture. It brings together visual programming concepts from Scratch, the functional purity of The Elm Architecture, and the modularity of Entity-Component-System (ECS) patterns.

## What is LogicCanvas?

LogicCanvas transforms game design from imperative code into a structured flow of Procedures, Tables (data), and Functions (pure logic). Instead of writing traditional game loops, you define:

- Tables: Immutable data structures (like `Paddle`, `Ball`, `Score`)
- Functions: Pure transformations that take input tables and produce output tables
- Procedures: Sequences of function calls that model game logic

The system automatically generates both:
- C code for native execution
- p5.js web simulations for instant browser-based testing

## Current Projects

Working examples demonstrating the architecture:

1. [Pong](pong.md) - Classic paddle game
2. [Snake](snake.md) - Collectible-based movement
3. [Quadtris](quadtris.md) - Block-based puzzle
4. [Breakout](breakout.md) - Brick-breaking arcade game

## Core Concepts

Simulations are a series of Procedures that produce immutable Tables using Functions.

Every game project is defined by:
- A YAML file describing tables, functions, and procedures
- A Markdown file documenting the game design
- Automatic code generation for both C and p5.js

Each project has Setup and Loop events, mirroring the classic game loop:

Each Procedure has:
- A name
- A list of tables it uses
- A list of functions it calls in sequence

A Table has:
- A name
- A list of columns
- Each column has a name and a type (int, float, bool, etc.)

A Function has:
- A name
- One or more input tables
- One or more output tables
- An optional list of parameters
- A body of code that uses the input tables and parameters to produce output tables
- Support for loops and conditionals
- Ability to call other functions

### Double-Buffering State Management

Functions are pure and have no side effects. They return new tables based on input tables.

The generated code uses double buffering: each table has a current and next state. Functions read from current tables and write to next tables, then the system swaps them. This ensures immutability and predictable execution order.

Example runtime structure (Arduino-style main loop):

```c
int main() {
  Setup();
  while (true) {
    Loop();
  }
}
```

## What Can It Become?

LogicCanvas aims to evolve into a visual game design environment where:

- Non-programmers can design game logic through node-based interfaces
- Developers can prototype rapidly with automatic code generation
- Educators can teach programming concepts through visual data flow
- AI systems can reason about and generate game mechanics declaratively

Potential future capabilities include:
- Multi-language generation (Rust, WebAssembly, TypeScript)
- Real-time visual debugging with state inspection
- Multiplayer networking generation from single-player definitions
- Asset pipeline integration for sprites, sounds, and animations
- Cross-platform deployment (web, desktop, mobile, embedded)
- AI-assisted game design and balancing

See [Improvements.md](Improvements.md) for the full roadmap of 50+ planned features.

---

## Philosophy: Visual & Modular Programming

Inspired by The Elm Architecture, ECS, and Scratch Programming Language.
How can we make programming more visual and modular?

Functions are pure and have no side effects. They return new tables based on input tables.

The generated code uses double buffering: each table has a current and next state. Functions read from current tables and write to next tables, then the system swaps them. This ensures immutability and predictable execution order.

Example generated structure:

```c
// Table definitions with double-buffering
struct Paddle { float x, y, width, height; };
struct Ball { float x, y, radius, speedX, speedY; };
struct Score { int player1, player2; };

Paddle paddle, paddle_next;    // Current and next state
Ball ball, ball_next;
Score score, score_next;

// Main game loop
int main() {
  Setup();
  while (true) {
    Loop();
  }
}

void Setup() {
  InitPaddle();   // Each procedure calls functions
  InitBall();
  InitScore();
}

void Loop() {
  MovePaddle();   // Functions read current, write next
  MoveBall();
  CheckScore();
  // After Loop completes, buffers swap automatically
}
```

## Getting Started

### Build & Run

```bash
go build
./webapp.exe  # or ./webapp on Linux/Mac
```

Then select a project from the dropdown and click "Run Project" to see it in action.

See [USAGE.md](USAGE.md) for detailed documentation on using the interface and creating new projects.

---

Start exploring with the existing games, then try designing your own using the visual canvas and YAML definitions!
