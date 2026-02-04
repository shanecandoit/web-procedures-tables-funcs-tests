import yaml
import sys
import os
import glob

def generate_c_code(data):
    project_name = data.get('project_name', 'Unnamed Project')
    code = []
    code.append(f"// Generated Code for Project: {project_name}")
    code.append("#include <stdbool.h>")
    code.append("#include <stdio.h>")
    code.append("#include <stdlib.h>")
    code.append("#include <math.h>\n")

    if 'config' in data:
        code.append("// --- Configuration Constants ---")
        for key, value in data['config'].items():
            # Handle float values by adding .0f if not present
            if isinstance(value, float):
                code.append(f"#define {key.upper()} {value}f")
            else:
                code.append(f"#define {key.upper()} {value}")
        code.append("")

    code.append("// --- Table Structures ---")
    for table_name, table_data in data.get('tables', {}).items():
        struct_name = f"{table_name.replace('_', '').capitalize()}Table"
        code.append(f"typedef struct {{")
        for col_name, col_type in table_data['columns'].items():
            if col_type == 'array':
                 code.append(f"    int {col_name}[100];")
            else:
                 code.append(f"    {col_type} {col_name};")
        code.append(f"}} {struct_name};\n")

    code.append("// --- Global State (Double Buffering) ---")
    code.append("struct GameState {")
    for table_name in data.get('tables', {}):
        struct_name = f"{table_name.replace('_', '').capitalize()}Table"
        code.append(f"    {struct_name} {table_name}_curr;")
        code.append(f"    {struct_name} {table_name}_next;")
    code.append("} state;\n")

    code.append("// --- Pure Logic Prototypes ---")
    for func_name, func_data in data.get('functions', {}).items():
        outputs = func_data.get('outputs', [])
        inputs = func_data.get('inputs', [])

        if len(outputs) == 1:
            ret_type = f"{outputs[0].replace('_', '').capitalize()}Table"
        else:
            ret_type = "void"

        params = []
        for inp in inputs:
             params.append(f"{inp.replace('_', '').capitalize()}Table {inp}_in")
        
        if len(outputs) > 1:
            for out in outputs:
                params.append(f"{out.replace('_', '').capitalize()}Table* {out}_out")

        param_str = ", ".join(params)
        code.append(f"{ret_type} Logic_{func_name}({param_str});")
    code.append("")

    code.append("// --- Generated Wrappers ---")
    for func_name, func_data in data.get('functions', {}).items():
        inputs = func_data.get('inputs', [])
        outputs = func_data.get('outputs', [])

        code.append(f"void Wrapper_{func_name}() {{")
        args = [f"state.{inp}_curr" for inp in inputs]
        
        if len(outputs) == 1:
            out_table = outputs[0]
            args_str = ", ".join(args)
            code.append(f"    state.{out_table}_next = Logic_{func_name}({args_str});")
            if "Init" in func_name:
                 code.append(f"    state.{out_table}_curr = state.{out_table}_next;")
        elif len(outputs) > 1:
            for out in outputs:
                # Note: this assumes the implementation handles pointers for multiple outputs
                args.append(f"&state.{out}_next")
            args_str = ", ".join(args)
            code.append(f"    Logic_{func_name}({args_str});")
            if "Init" in func_name:
                for out in outputs:
                    code.append(f"    state.{out}_curr = state.{out}_next;")
        else:
            args_str = ", ".join(args)
            code.append(f"    Logic_{func_name}({args_str});")

        code.append("}\n")

    code.append("// --- Buffer Swap ---")
    code.append("void Swap_Buffers() {")
    for table_name in data.get('tables', {}):
        code.append(f"    state.{table_name}_curr = state.{table_name}_next;")
    code.append("}\n")

    code.append("// --- High Level Procedures ---")
    for proc_name, func_list in data.get('procedures', {}).items():
        code.append(f"void {proc_name}() {{")
        for func in func_list:
            code.append(f"    Wrapper_{func}();")
        if proc_name == "Loop":
             code.append("    Swap_Buffers();")
        code.append("}\n")

    code.append("int main() {")
    code.append("    Setup();")
    code.append("    while (true) {")
    code.append("        Loop();")
    code.append("    }")
    code.append("    return 0;")
    code.append("}")

    return "\n".join(code)

def get_game_logic(project_name):
    # Returns (html_logic, draw_logic, game_specific_css, game_specific_ui)
    
    if project_name.lower() == 'pong':
        html_logic = """
    function Logic_InitPaddles() {
        const p1 = { x: 40, y: (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2), width: PADDLE_WIDTH, height: PADDLE_HEIGHT };
        const p2 = { x: SCREEN_WIDTH - 40 - PADDLE_WIDTH, y: (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2), width: PADDLE_WIDTH, height: PADDLE_HEIGHT };
        return { paddle1: p1, paddle2: p2 };
    }
    function Logic_InitBall() {
        return { x: SCREEN_WIDTH / 2, y: SCREEN_HEIGHT / 2, radius: BALL_RADIUS, speedX: BALL_START_SPEED_X, speedY: BALL_START_SPEED_Y };
    }
    function Logic_InitScore() { return { p1: 0, p2: 0 }; }
    function Logic_MovePaddle1(p) {
        let p_out = { ...p };
        if (keyIsDown(87) || keyIsDown(UP_ARROW)) p_out.y -= PADDLE_SPEED;
        if (keyIsDown(83) || keyIsDown(DOWN_ARROW)) p_out.y += PADDLE_SPEED;
        p_out.y = Math.max(0, Math.min(SCREEN_HEIGHT - p_out.height, p_out.y));
        return p_out;
    }
    function Logic_MovePaddle2(p, b) {
        let p_out = { ...p };
        const paddleCenter = p_out.y + p_out.height / 2;
        const deadzone = 10;
        if (b.y > paddleCenter + deadzone) p_out.y += PADDLE_SPEED * 0.85;
        else if (b.y < paddleCenter - deadzone) p_out.y -= PADDLE_SPEED * 0.85;
        p_out.y = Math.max(0, Math.min(SCREEN_HEIGHT - p_out.height, p_out.y));
        return p_out;
    }
    function Logic_MoveBall(b, p1, p2) {
        let b_out = { ...b };
        b_out.x += b_out.speedX;
        b_out.y += b_out.speedY;
        if (b_out.y - b_out.radius <= 0 || b_out.y + b_out.radius >= SCREEN_HEIGHT) {
            b_out.speedY *= -1;
            b_out.y = b_out.y <= 0 ? b_out.radius : SCREEN_HEIGHT - b_out.radius;
        }
        if (b_out.speedX < 0) {
            let hitX = (b_out.x - b_out.radius <= p1.x + p1.width) && (b_out.x + b_out.radius >= p1.x);
            let hitY = (b_out.y >= p1.y) && (b_out.y <= p1.y + p1.height);
            if (hitX && hitY) { b_out.speedX *= -1.05; b_out.x = p1.x + p1.width + b_out.radius; }
        }
        if (b_out.speedX > 0) {
            let hitX = (b_out.x + b_out.radius >= p2.x) && (b_out.x - b_out.radius <= p2.x + p2.width);
            let hitY = (b_out.y >= p2.y) && (b_out.y <= p2.y + p2.height);
            if (hitX && hitY) { b_out.speedX *= -1.05; b_out.x = p2.x - b_out.radius; }
        }
        if (b_out.x < 0 || b_out.x > SCREEN_WIDTH) return Logic_InitBall(); 
        return b_out;
    }
    function Logic_CheckScore(b, s) {
        let s_out = { ...s };
        if (b.x < 0) s_out.p2 += 1;
        if (b.x > SCREEN_WIDTH) s_out.p1 += 1;
        return s_out;
    }
    function Logic_GameLost() {}
    function Logic_GameWon() {}
"""
        draw_logic = """
        // Draw logic
        stroke(51, 65, 85);
        strokeWeight(4);
        for(let i=0; i<height; i+=40) line(width/2, i+10, width/2, i+30);
        noStroke();
        drawingContext.shadowBlur = 15;
        drawingContext.shadowColor = '#38bdf8';
        fill(255);
        rect(state.paddle1_curr.x, state.paddle1_curr.y, state.paddle1_curr.width, state.paddle1_curr.height, 4);
        drawingContext.shadowColor = '#fbbf24';
        fill('#fbbf24');
        rect(state.paddle2_curr.x, state.paddle2_curr.y, state.paddle2_curr.width, state.paddle2_curr.height, 4);
        drawingContext.shadowBlur = 20;
        drawingContext.shadowColor = '#ec4899';
        fill('#ec4899');
        circle(state.ball_curr.x, state.ball_curr.y, state.ball_curr.radius * 2);
        drawingContext.shadowBlur = 0;
        fill('#f8fafc');
        textSize(48); textAlign(CENTER); textFont('Inter'); textStyle(BOLD);
        text(state.score_curr.p1, width/4, 80);
        text(state.score_curr.p2, 3 * width/4, 80);
"""
        return html_logic, draw_logic, "h1 { color: #38bdf8; }", "<p>Player (WS Keys) vs CPU</p>"

    elif project_name.lower() == 'snake':
        html_logic = """
    function Logic_InitSnakeHead() {
        return { x: Math.floor(SCREEN_WIDTH / (2 * GRID_SIZE)) * GRID_SIZE, y: Math.floor(SCREEN_HEIGHT / (2 * GRID_SIZE)) * GRID_SIZE, directionX: 1, directionY: 0, size: GRID_SIZE };
    }
    function Logic_InitSnakeBody() {
        const headX = Math.floor(SCREEN_WIDTH / (2 * GRID_SIZE)) * GRID_SIZE;
        const headY = Math.floor(SCREEN_HEIGHT / (2 * GRID_SIZE)) * GRID_SIZE;
        return { pos_x: [headX - GRID_SIZE, headX - 2 * GRID_SIZE, headX - 3 * GRID_SIZE], pos_y: [headY, headY, headY], length: 3 };
    }
    function Logic_InitSnacks() {
        return { x: Math.floor(Math.random() * (SCREEN_WIDTH / GRID_SIZE)) * GRID_SIZE, y: Math.floor(Math.random() * (SCREEN_HEIGHT / GRID_SIZE)) * GRID_SIZE, radius: GRID_SIZE / 2, active: 1 };
    }
    function Logic_InitScore() { return { points: 0, highScore: 0 }; }
    function Logic_InitTimer() { return { elapsed: 0, gameState: 0 }; }
    function Logic_UpdateTimer(t) {
        let t_out = { ...t };
        if (t_out.gameState === 0) t_out.elapsed += 1;
        return t_out;
    }
    function Logic_ProcessInput(h) {
        let h_out = { ...h };
        if (keyIsDown(LEFT_ARROW) && h.directionX !== 1) { h_out.directionX = -1; h_out.directionY = 0; }
        else if (keyIsDown(RIGHT_ARROW) && h.directionX !== -1) { h_out.directionX = 1; h_out.directionY = 0; }
        else if (keyIsDown(UP_ARROW) && h.directionY !== 1) { h_out.directionX = 0; h_out.directionY = -1; }
        else if (keyIsDown(DOWN_ARROW) && h.directionY !== -1) { h_out.directionX = 0; h_out.directionY = 1; }
        return h_out;
    }
    function Logic_MoveSnakeHead(h, t) {
        if (t.gameState !== 0) return h;
        if (frameCount % 6 !== 0) return h;
        let h_out = { ...h };
        h_out.x += h.directionX * GRID_SIZE;
        h_out.y += h.directionY * GRID_SIZE;
        return h_out;
    }
    function Logic_MoveSnakeBody(h, b, t) {
        if (t.gameState !== 0) return b;
        if (frameCount % 6 !== 0) return b;
        let b_out = { ...b, pos_x: [...b.pos_x], pos_y: [...b.pos_y] };
        for (let i = b_out.length - 1; i > 0; i--) { b_out.pos_x[i] = b_out.pos_x[i-1]; b_out.pos_y[i] = b_out.pos_y[i-1]; }
        b_out.pos_x[0] = h.x; b_out.pos_y[0] = h.y;
        return b_out;
    }
    function Logic_CheckSnackCollision(h, b, s) {
        let b_out = { ...b, pos_x: [...b.pos_x], pos_y: [...b.pos_y] };
        let s_out = { ...s };
        if (h.x === s.x && h.y === s.y) {
            b_out.length += 1;
            b_out.pos_x.push(b.pos_x[b.length-1]);
            b_out.pos_y.push(b.pos_y[b.length-1]);
            s_out.active = 0;
        }
        return { snake_body: b_out, snacks: s_out };
    }
    function Logic_CheckWallCollision(h, t) {
        let t_out = { ...t };
        if (h.x < 0 || h.x >= SCREEN_WIDTH || h.y < 0 || h.y >= SCREEN_HEIGHT) { t_out.gameState = 2; }
        return t_out;
    }
    function Logic_CheckSelfCollision(h, b, t) {
        let t_out = { ...t };
        for (let i = 0; i < b.length; i++) { if (h.x === b.pos_x[i] && h.y === b.pos_y[i]) t_out.gameState = 2; }
        return t_out;
    }
    function Logic_UpdateScore(sc, sn) {
        let sc_out = { ...sc };
        if (sn.active === 0) { sc_out.points += 10; if (sc_out.points > sc_out.highScore) sc_out.highScore = sc_out.points; }
        return sc_out;
    }
    function Logic_SpawnSnack(s, b) {
        if (s.active === 1) return s;
        let s_out = { ...s, active: 1 };
        let valid = false;
        while (!valid) {
            s_out.x = Math.floor(Math.random() * (SCREEN_WIDTH / GRID_SIZE)) * GRID_SIZE;
            s_out.y = Math.floor(Math.random() * (SCREEN_HEIGHT / GRID_SIZE)) * GRID_SIZE;
            valid = true;
            for (let i = 0; i < b.length; i++) { if (s_out.x === b.pos_x[i] && s_out.y === b.pos_y[i]) { valid = false; break; } }
        }
        return s_out;
    }
"""
        draw_logic = """
        if (state.timer_curr.gameState === 2) {
            document.getElementById('game-over').style.display = 'block';
            document.getElementById('final-score').textContent = 'Score: ' + state.score_curr.points;
            return;
        }
        stroke(31, 41, 55);
        for(let x=0; x<width; x+=GRID_SIZE) line(x, 0, x, height);
        for(let y=0; y<height; y+=GRID_SIZE) line(0, y, width, y);
        noStroke();
        drawingContext.shadowBlur = 15;
        drawingContext.shadowColor = '#f43f5e';
        fill('#f43f5e');
        rect(state.snacks_curr.x + 2, state.snacks_curr.y + 2, GRID_SIZE - 4, GRID_SIZE - 4, 4);
        drawingContext.shadowColor = '#10b981';
        fill('#10b981');
        for (let i = 0; i < state.snake_body_curr.length; i++) {
            rect(state.snake_body_curr.pos_x[i] + 1, state.snake_body_curr.pos_y[i] + 1, GRID_SIZE - 2, GRID_SIZE - 2, 4);
        }
        drawingContext.shadowBlur = 20;
        drawingContext.shadowColor = '#34d399';
        fill('#34d399');
        rect(state.snake_head_curr.x, state.snake_head_curr.y, GRID_SIZE, GRID_SIZE, 4);
        drawingContext.shadowBlur = 0;
        fill('#f8fafc');
        textSize(24); textAlign(LEFT); textFont('Inter');
        text('Score: ' + state.score_curr.points, 20, 40);
        textAlign(RIGHT); text('High Score: ' + state.score_curr.highScore, width - 20, 40);
"""
        return html_logic, draw_logic, "h1 { color: #10b981; }", "<p>Use Arrow Keys to Navigate</p><div id='game-over' class='game-over'><h2>GAME OVER</h2><p id='final-score'>Score: 0</p><button onclick='resetGame()'>Try Again</button></div>"

    else:
        # Default / Generic
        return "// Generic Logic Placeholder", "    text('Generic Visualization for ' + project_name, 20, 40);", "", "<p>Generic Project View</p>"

def generate_html_code(data):
    project_name = data.get('project_name', 'Unnamed Project')
    config = data.get('config', {})
    width = config.get('screen_width', 800)
    height = config.get('screen_height', 600)
    
    html_logic, draw_logic, game_css, game_ui = get_game_logic(project_name)

    html = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <style>
        body {{ margin: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; background: #0f172a; overflow: hidden; color: #f8fafc; font-family: 'Inter', system-ui, sans-serif; }}
        canvas {{ box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); border: 4px solid #334155; border-radius: 12px; }}
        #ui {{ margin-bottom: 2rem; text-align: center; }}
        h1 {{ margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -0.025em; }}
        p {{ color: #94a3b8; margin-top: 0.5rem; }}
        .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(15, 23, 42, 0.9); padding: 2rem; border-radius: 12px; border: 2px solid #ef4444; text-align: center; display: none; z-index: 100; }}
        .game-over h2 {{ color: #ef4444; margin: 0 0 1rem; }}
        .game-over button {{ background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: bold; }}
        {game_css}
    </style>
</head>
<body>
    <div id="ui">
        <h1>{project_name}</h1>
        {game_ui}
    </div>
    <script>
"""]

    html.append("    // --- Configuration ---")
    html.append(f"    const SCREEN_WIDTH = {width};")
    html.append(f"    const SCREEN_HEIGHT = {height};")
    for key, value in config.items():
        if key.upper() not in ['SCREEN_WIDTH', 'SCREEN_HEIGHT']:
            html.append(f"    const {key.upper()} = {value};")
    html.append("")

    html.append("    // --- Global State ---")
    state_init = "{\n"
    for table_name in data.get('tables', {}):
        state_init += f"        {table_name}_curr: {{}},\n"
        state_init += f"        {table_name}_next: {{}},\n"
    state_init += "    }"
    html.append(f"    let state = {state_init};\n")

    html.append("    // --- Pure Logic Functions ---")
    html.append(html_logic)

    html.append("    // --- Generated Wrappers ---")
    for func_name, func_data in data.get('functions', {}).items():
        inputs = func_data.get('inputs', [])
        outputs = func_data.get('outputs', [])
        
        html.append(f"    function Wrapper_{func_name}() {{")
        args = [f"state.{inp}_curr" for inp in inputs]
        args_str = ", ".join(args)
        
        if len(outputs) == 1:
            out_table = outputs[0]
            html.append(f"        state.{out_table}_next = Logic_{func_name}({args_str});")
            if "Init" in func_name:
                html.append(f"        state.{out_table}_curr = state.{out_table}_next;")
        elif len(outputs) > 1:
            html.append(f"        const results = Logic_{func_name}({args_str});")
            for out in outputs:
                html.append(f"        state.{out}_next = results.{out};")
                if "Init" in func_name:
                    html.append(f"        state.{out}_curr = state.{out}_next;")
        else:
            html.append(f"        Logic_{func_name}({args_str});")
        html.append("    }\n")

    html.append("    // --- Procedures ---")
    html.append("    function SwapBuffers() {")
    for table_name in data.get('tables', {}):
        # Deep copy for arrays if needed
        html.append(f"        state.{table_name}_curr = {{ ...state.{table_name}_next, pos_x: state.{table_name}_next.pos_x ? [...state.{table_name}_next.pos_x]:undefined, pos_y: state.{table_name}_next.pos_y ? [...state.{table_name}_next.pos_y]:undefined }};")
    html.append("    }\n")

    for proc_name, func_list in data.get('procedures', {}).items():
        html.append(f"    function {proc_name}() {{")
        for func in func_list:
            html.append(f"        Wrapper_{func}();")
        if proc_name == "Loop":
            html.append("        SwapBuffers();")
        html.append("    }\n")

    html.append(f"""    // --- p5.js Lifecycle ---
    function setup() {{
        createCanvas(SCREEN_WIDTH, SCREEN_HEIGHT);
        const project_name = '{project_name}';
        Setup();
    }}

    function draw() {{
        background(15, 23, 42);
        Loop();
        {draw_logic}
    }}

    function resetGame() {{
        if(document.getElementById('game-over')) document.getElementById('game-over').style.display = 'none';
        Setup();
    }}
    </script>
</body>
</html>
""")

    return "\n".join(html)

def main():
    target_dir = 'generated'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    yaml_files = glob.glob("*.yaml")
    if not yaml_files:
        print("No YAML files found in the current directory.")
        return

    for yaml_path in yaml_files:
        project_name = os.path.splitext(os.path.basename(yaml_path))[0]
        print(f"Processing project: {project_name}...")

        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"  Error reading {yaml_path}: {e}")
            continue

        # Generate C
        try:
            generated_c = generate_c_code(data)
            c_output = os.path.join(target_dir, f"{project_name}_code.c")
            with open(c_output, 'w') as f:
                f.write(generated_c)
            print(f"  Generated {c_output}")
        except Exception as e:
            print(f"  Error generating C for {project_name}: {e}")

        # Generate HTML
        try:
            generated_html = generate_html_code(data)
            html_output = os.path.join(target_dir, f"{project_name}_code.html")
            with open(html_output, 'w') as f:
                f.write(generated_html)
            print(f"  Generated {html_output}")
        except Exception as e:
            print(f"  Error generating HTML for {project_name}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
