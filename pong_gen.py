import yaml
import sys

def generate_c_code(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    code = []
    code.append(f"// Generated Code for Project: {data.get('project_name', 'Unnamed Project')}")
    code.append("#include <stdbool.h>")
    code.append("#include <stdio.h>\n")

    if 'config' in data:
        code.append("// --- Configuration Constants ---")
        for key, value in data['config'].items():
            code.append(f"#define {key.upper()} {value}")
        code.append("")

    code.append("// --- Table Structures ---")
    for table_name, table_data in data.get('tables', {}).items():
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"typedef struct {{")
        for col_name, col_type in table_data['columns'].items():
            code.append(f"    {col_type} {col_name};")
        code.append(f"}} {struct_name};\n")

    code.append("// --- Global State (Double Buffering) ---")
    code.append("struct GameState {")
    for table_name in data.get('tables', {}):
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"    {struct_name} {table_name}_curr;")
        code.append(f"    {struct_name} {table_name}_next;")
    code.append("} state;\n")

    code.append("// --- Pure Logic Prototypes (User Implemented) ---")
    for func_name, func_data in data.get('functions', {}).items():
        outputs = func_data.get('outputs', [])
        inputs = func_data.get('inputs', [])

        if len(outputs) == 1:
            ret_type = f"{outputs[0].capitalize()}Table"
        else:
            ret_type = "void"

        params = []
        for inp in inputs:
             params.append(f"{inp.capitalize()}Table {inp}_in")
        
        if len(outputs) > 1:
            for out in outputs:
                params.append(f"{out.capitalize()}Table* {out}_out")

        param_str = ", ".join(params)
        code.append(f"{ret_type} Logic_{func_name}({param_str});")
    code.append("")

    code.append("// --- Generated Wrappers (The Wiring) ---")
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

    code.append("// --- Main Entry Point ---")
    code.append("int main() {")
    code.append("    Setup();")
    code.append("    while (true) {")
    code.append("        Loop();")
    code.append("    }")
    code.append("    return 0;")
    code.append("}")

    return "\n".join(code)

def generate_html_code(data):
    project_name = data.get('project_name', 'Unnamed Project')
    config = data.get('config', {})
    width = config.get('screen_width', 800)
    height = config.get('screen_height', 600)

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
        h1 {{ margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -0.025em; color: #38bdf8; }}
        p {{ color: #94a3b8; margin-top: 0.5rem; }}
        .controls {{ position: absolute; bottom: 20px; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div id="ui">
        <h1>{project_name}</h1>
        <p>Player (WS Keys) vs CPU</p>
    </div>
    <div class="controls">Use W and S to move your paddle</div>
    <script>
"""]

    html.append("    // --- Configuration ---")
    for key, value in config.items():
        html.append(f"    const {key.upper()} = {value};")
    html.append("")

    html.append("    // --- Global State ---")
    state_init = "{\n"
    for table_name in data.get('tables', {}):
        state_init += f"        {table_name}_curr: {{}},\n"
        state_init += f"        {table_name}_next: {{}},\n"
    state_init += "    }"
    html.append(f"    let state = {state_init};\n")

    html.append("""    // --- Pure Logic Functions ---
    function Logic_InitPaddles() {
        const p1 = {
            x: 40,
            y: (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2),
            width: PADDLE_WIDTH,
            height: PADDLE_HEIGHT
        };
        const p2 = {
            x: SCREEN_WIDTH - 40 - PADDLE_WIDTH,
            y: (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2),
            width: PADDLE_WIDTH,
            height: PADDLE_HEIGHT
        };
        return { paddle1: p1, paddle2: p2 };
    }

    function Logic_InitBall() {
        return {
            x: SCREEN_WIDTH / 2,
            y: SCREEN_HEIGHT / 2,
            radius: BALL_RADIUS,
            speedX: BALL_START_SPEED_X,
            speedY: BALL_START_SPEED_Y
        };
    }

    function Logic_InitScore() {
        return { p1: 0, p2: 0 };
    }

    function Logic_MovePaddle1(p) {
        let p_out = { ...p };
        // Player Control
        if (keyIsDown(87) || keyIsDown(UP_ARROW)) { // W or Up
            p_out.y -= PADDLE_SPEED;
        }
        if (keyIsDown(83) || keyIsDown(DOWN_ARROW)) { // S or Down
            p_out.y += PADDLE_SPEED;
        }
        p_out.y = Math.max(0, Math.min(SCREEN_HEIGHT - p_out.height, p_out.y));
        return p_out;
    }

    function Logic_MovePaddle2(p, b) {
        let p_out = { ...p };
        // Improved AI: follow the ball with a deadzone to prevent glitchy jitter
        const paddleCenter = p_out.y + p_out.height / 2;
        const deadzone = 10;
        
        if (b.y > paddleCenter + deadzone) {
            p_out.y += PADDLE_SPEED * 0.85; // Slightly slower than player
        } else if (b.y < paddleCenter - deadzone) {
            p_out.y -= PADDLE_SPEED * 0.85;
        }
        p_out.y = Math.max(0, Math.min(SCREEN_HEIGHT - p_out.height, p_out.y));
        return p_out;
    }

    function Logic_MoveBall(b, p1, p2) {
        let b_out = { ...b };
        b_out.x += b_out.speedX;
        b_out.y += b_out.speedY;

        // Top/Bottom walls
        if (b_out.y - b_out.radius <= 0 || b_out.y + b_out.radius >= SCREEN_HEIGHT) {
            b_out.speedY *= -1;
            b_out.y = b_out.y <= 0 ? b_out.radius : SCREEN_HEIGHT - b_out.radius;
        }

        // Paddle 1 Collision (Left)
        if (b_out.speedX < 0) {
            let hitX = (b_out.x - b_out.radius <= p1.x + p1.width) && (b_out.x + b_out.radius >= p1.x);
            let hitY = (b_out.y >= p1.y) && (b_out.y <= p1.y + p1.height);
            if (hitX && hitY) {
                b_out.speedX *= -1.05;
                b_out.x = p1.x + p1.width + b_out.radius;
            }
        }

        // Paddle 2 Collision (Right)
        if (b_out.speedX > 0) {
            let hitX = (b_out.x + b_out.radius >= p2.x) && (b_out.x - b_out.radius <= p2.x + p2.width);
            let hitY = (b_out.y >= p2.y) && (b_out.y <= p2.y + p2.height);
            if (hitX && hitY) {
                b_out.speedX *= -1.05;
                b_out.x = p2.x - b_out.radius;
            }
        }

        // Reset and Score points
        if (b_out.x < 0 || b_out.x > SCREEN_WIDTH) {
            return Logic_InitBall(); 
        }

        return b_out;
    }

    function Logic_CheckScore(b, s) {
        let s_out = { ...s };
        if (b.x < 0) s_out.p2 += 1;
        if (b.x > SCREEN_WIDTH) s_out.p1 += 1;
        return s_out;
    }

    function Logic_GameLost(s) {}
    function Logic_GameWon(s) {}
""")

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
        html.append(f"        state.{table_name}_curr = {{ ...state.{table_name}_next }};")
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
        createCanvas({width}, {height});
        Setup();
    }}

    function draw() {{
        background(15, 23, 42);
        Loop();
        
        // --- Draw logic ---
        stroke(51, 65, 85);
        strokeWeight(4);
        for(let i=0; i<height; i+=40) line(width/2, i+10, width/2, i+30);

        noStroke();
        drawingContext.shadowBlur = 15;
        drawingContext.shadowColor = '#38bdf8';
        
        fill(255);
        // Player
        rect(state.paddle1_curr.x, state.paddle1_curr.y, state.paddle1_curr.width, state.paddle1_curr.height, 4);
        
        drawingContext.shadowColor = '#fbbf24';
        fill('#fbbf24');
        // CPU
        rect(state.paddle2_curr.x, state.paddle2_curr.y, state.paddle2_curr.width, state.paddle2_curr.height, 4);
        
        drawingContext.shadowBlur = 20;
        drawingContext.shadowColor = '#ec4899';
        fill('#ec4899');
        circle(state.ball_curr.x, state.ball_curr.y, state.ball_curr.radius * 2);

        drawingContext.shadowBlur = 0;
        fill('#f8fafc');
        textSize(48);
        textAlign(CENTER);
        textFont('Inter');
        textStyle(BOLD);
        text(state.score_curr.p1, width/4, 80);
        text(state.score_curr.p2, 3 * width/4, 80);
    }}
    </script>
</body>
</html>
""")

    return "\n".join(html)

if __name__ == "__main__":
    yaml_path = 'pong.yaml'
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Generate C
    generated_c = generate_c_code(yaml_path)
    c_output = 'pong_code.c'
    with open(c_output, 'w') as f:
        f.write(generated_c)
    
    # Generate HTML
    generated_html = generate_html_code(data)
    html_output = 'pong_code.html'
    with open(html_output, 'w') as f:
        f.write(generated_html)
    
    print(f"Successfully generated {c_output} and {html_output} from {yaml_path}")
