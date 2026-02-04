package main

import (
	"fmt"
	"os"

	webview "github.com/webview/webview_go"
)

func main() {
	// Read pong.md
	mdContent, err := os.ReadFile("pong.md")
	if err != nil {
		fmt.Printf("Error reading pong.md: %v\n", err)
		return
	}

	// Read pong.yaml
	yamlContent, err := os.ReadFile("pong.yaml")
	if err != nil {
		// If yaml doesn't exist yet, we still want to run
		yamlContent = []byte("# pong.yaml not found")
	}

	// Create webview
	debug := true
	w := webview.New(debug)
	defer w.Destroy()

	w.SetTitle("Pong Implementation - Web UI")
	w.SetSize(1400, 900, 0)

	// Prepare HTML
	html := fmt.Sprintf(`
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Pong Implementation</title>
			<style>
				:root {
					--bg: #0f172a;
					--card-bg: rgba(30, 41, 59, 0.7);
					--text: #e0e0e0;
					--primary: #60a5fa;
					--secondary: #a855f7;
					--border: rgba(255, 255, 255, 0.1);
				}
				body {
					font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
					line-height: 1.6;
					color: var(--text);
					background-color: var(--bg);
					margin: 0;
					padding: 2rem;
					display: flex;
					justify-content: center;
				}
				.container {
					max-width: 1200px;
					width: 100%%;
					display: grid;
					grid-template-columns: 1fr 1fr;
					gap: 2rem;
				}
				.panel {
					background: var(--card-bg);
					backdrop-filter: blur(10px);
					padding: 2rem;
					border-radius: 12px;
					box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
					border: 1px solid var(--border);
					display: flex;
					flex-direction: column;
					height: 85vh;
				}
				h1, h2 {
					margin-top: 0;
					background: linear-gradient(to right, var(--primary), var(--secondary));
					-webkit-background-clip: text;
					-webkit-text-fill-color: transparent;
					font-weight: 800;
				}
				pre {
					background: #000000;
					padding: 1rem;
					border-radius: 8px;
					overflow: auto;
					font-family: 'Fira Code', 'Courier New', monospace;
					font-size: 0.85rem;
					border: 1px solid #334155;
					white-space: pre-wrap;
					flex-grow: 1;
				}
				.status {
					margin-top: 1rem;
					font-size: 0.75rem;
					color: #94a3b8;
					text-align: right;
				}
			</style>
		</head>
		<body>
			<div class="container">
				<div class="panel">
					<h2>pong.yaml</h2>
					<pre id="yaml-content"></pre>
					<div class="status">Synthesized Spec</div>
				</div>
				<div class="panel">
					<h2>pong.md</h2>
					<pre id="md-content"></pre>
					<div class="status">Original Documentation</div>
				</div>
			</div>
			<script>
				document.getElementById('yaml-content').textContent = %q;
				document.getElementById('md-content').textContent = %q;
			</script>
		</body>
		</html>
	`, string(yamlContent), string(mdContent))

	w.SetHtml(html)

	w.Run()
}
