# Usage Guide: LogicCanvas

Welcome to LogicCanvas, a powerful web-based environment for designing and generating games using a Procedures, Tables, and Functions (PTF) architecture.

## Getting Started

### Prerequisites
- Go: Required to compile and run the main application.
- Python 3: Required for the code generation scripts.
- C Compiler (GCC): Required if you intend to compile the generated C code manually.
- Webview Dependencies: Depending on your OS, you may need specific libraries (e.g., GTK for Linux).

### Installation & Build
To build the application:
```bash
go build
```
This will create `web-procedures-tables-funcs-tests.exe` (on Windows) or `web-procedures-tables-funcs-tests` (on unix systems).

## Using the Interface

1. Run the Application: Execute `./web-procedures-tables-funcs-tests.exe`.
2. Project Selector: Use the dropdown in the top-left to switch between projects (Pong, Snake, Breakout, Quadtris).
3. Project View: View the `.md` documentation and `.yaml` definition for the current project.
4. Canvas View: Visualize the data flow.
   - Blue Nodes: Tables (Data)
   - Green Nodes: Functions (Logic)
   - Arrows: Indicate the flow of inputs and outputs.
5. Run Project: Click the "Run Project" button to generate the latest code and play the game in the embedded viewer.

## Project Structure

A project consists of three core files:

- `{name}.yaml`: The machine-readable definition of the game's state (tables), procedures, and functions.
- `{name}.md`: Human-readable documentation of the game's design.
- Logic Implementation: The generator handles the visualization, but the logic functions are defined in the YAML.

## Adding a New Project

To add a new project called "MyGame":
1. Create a `MyGame.yaml` following the schema in `pong.yaml`.
2. Create a `MyGame.md` describing your game.
3. Restart LogicCanvas or use the dropdown to select "MyGame".
4. The system will automatically detect the new YAML and allow you to visualize and run it (using the generic generator for unknown projects).

## Code Generation

The `code_gen.py` script automatically:
- Scans for all `.yaml` files.
- Generates C code into `generated/{name}_code.c`.
- Generates a p5.js HTML simulation into `generated/{name}_code.html`.
- Implements Double Buffering state management for all generated code.
