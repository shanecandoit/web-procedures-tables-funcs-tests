import yaml
import sys

def generate_c_code(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    code = []

    # --- 1. Header & Type Definitions ---
    code.append(f"// Generated Code for Project: {data.get('project_name', 'Unnamed Project')}")
    code.append("#include <stdbool.h>")
    code.append("#include <stdio.h>\n")

    # Generate Config Constants
    if 'config' in data:
        code.append("// --- Configuration Constants ---")
        for key, value in data['config'].items():
            code.append(f"#define {key.upper()} {value}")
        code.append("")

    # Generate Structs for Tables
    code.append("// --- Table Structures ---")
    for table_name, table_data in data.get('tables', {}).items():
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"typedef struct {{")
        for col_name, col_type in table_data['columns'].items():
            code.append(f"    {col_type} {col_name};")
        code.append(f"}} {struct_name};\n")

    # --- 2. Global State (Double Buffering) ---
    code.append("// --- Global State (Double Buffered) ---")
    code.append("struct GameState {")
    for table_name in data.get('tables', {}):
        struct_name = f"{table_name.capitalize()}Table"
        code.append(f"    {struct_name} {table_name}_curr;")
        code.append(f"    {struct_name} {table_name}_next;")
    code.append("} state;\n")

    # --- 3. Pure Logic Function Prototypes ---
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

        param_str = ", ".join(params)
        code.append(f"{ret_type} Logic_{func_name}({param_str});")
    code.append("")

    # --- 4. Generated Wrappers (The Wiring) ---
    code.append("// --- Generated Wrappers (The Wiring) ---")
    for func_name, func_data in data.get('functions', {}).items():
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
        else:
            # Handle void return or multiple outputs (though yaml shows 0 or 1 usually)
            code.append(f"    Logic_{func_name}({args_str});")

        code.append("}\n")

    # --- 5. Buffer Swap Logic ---
    code.append("// --- Buffer Swap ---")
    code.append("void Swap_Buffers() {")
    for table_name in data.get('tables', {}):
        code.append(f"    state.{table_name}_curr = state.{table_name}_next;")
    code.append("}\n")

    # --- 6. Procedures (Setup / Loop) ---
    code.append("// --- High Level Procedures ---")
    for proc_name, func_list in data.get('procedures', {}).items():
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


def generate_html_code(data):
    project_name = data.get('project_name', 'Unnamed Project')
    
    # Extract config
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
        body {{ margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #121212; overflow: hidden; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        canvas {{ box-shadow: 0 0 20px rgba(0,0,0,0.5); border-radius: 8px; }}
        #ui {{ position: absolute; top: 20px; text-align: center; width: 100%; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="ui"><h1>{project_name}</h1></div>
    <script>
"""]

    # 1. Config
    html.append("    // --- Configuration ---")
    for key, value in config.items():
        html.append(f"    const {key.upper()} = {value};")
    html.append("")

    # 2. State Container
    html.append("    // --- Global State ---")
    state_init = "{\n"
    for table_name in data.get('tables', {}):
        state_init += f"        {table_name}_curr: {{}},\n"
        state_init += f"        {table_name}_next: {{}},\n"
    state_init += "    }"
    html.append(f"    let state = {state_init};\n")

    # 3. Logic Implementation (Hardcoded based on pong.md for functional demo)
    html.append("""    // --- Pure Logic Functions ---
    function Logic_InitPaddle() {
        return {
            x: 30,
            y: (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2),
            width: PADDLE_WIDTH,
            height: PADDLE_HEIGHT
        };
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

    function Logic_MovePaddle(p) {
        let p_out = { ...p };
        // Simple AI: follow the ball
        if (state.ball_curr.y > p_out.y + p_out.height / 2) {
            p_out.y += PADDLE_SPEED;
        } else {
            p_out.y -= PADDLE_SPEED;
        }
        // Constraint
        p_out.y = Math.max(0, Math.min(SCREEN_HEIGHT - p_out.height, p_out.y));
        return p_out;
    }

    function Logic_MoveBall(b, p) {
        let b_out = { ...b };
        b_out.x += b_out.speedX;
        b_out.y += b_out.speedY;

        // Top/Bottom walls
        if (b_out.y - b_out.radius <= 0 || b_out.y + b_out.radius >= SCREEN_HEIGHT) {
            b_out.speedY *= -1;
        }

        // Paddle Collision
        let hitX = (b_out.x - b_out.radius <= p.x + p.width) && (b_out.x + b_out.radius >= p.x);
        let hitY = (b_out.y >= p.y) && (b_out.y <= p.y + p.height);
        
        if (hitX && hitY) {
            b_out.speedX *= -1.05;
            b_out.x = p.x + p.width + b_out.radius;
        }

        // Reset if out of bounds (for continuous play)
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

    # 4. Generated Wrappers
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
        else:
            html.append(f"        Logic_{func_name}({args_str});")
        html.append("    }\n")

    # 5. Procedures
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

    # 6. p5.js Integration
    html.append(f"""    // --- p5.js Lifecycle ---
    function setup() {{
        createCanvas({width}, {height});
        Setup();
    }}

    function draw() {{
        background(20, 20, 25);
        Loop();
        
        // --- Draw logic ---
        stroke(100);
        strokeWeight(2);
        for(let i=0; i<height; i+=40) line(width/2, i, width/2, i+20);

        noStroke();
        fill(255);
        rect(state.paddle_curr.x, state.paddle_curr.y, state.paddle_curr.width, state.paddle_curr.height);
        
        fill(255, 100, 100);
        circle(state.ball_curr.x, state.ball_curr.y, state.ball_curr.radius * 2);

        fill(200);
        textSize(32);
        textAlign(CENTER);
        text(state.score_curr.p1 + "   " + state.score_curr.p2, width/2, 50);
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
    generated_c = generate_c_code(yaml_path) # Keeping original func signature for consistency or updating it
    c_output = 'pong_code.c'
    with open(c_output, 'w') as f:
        f.write(generated_c)
    
    # Generate HTML
    generated_html = generate_html_code(data)
    html_output = 'pong_code.html'
    with open(html_output, 'w') as f:
        f.write(generated_html)
    
    print(f"Successfully generated {c_output} and {html_output} from {yaml_path}")
