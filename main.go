package main

import (
	"fmt"
	"os"
	"os/exec"

	webview "github.com/webview/webview_go"
)

type ProjectData struct {
	Name string `json:"name"`
	MD   string `json:"md"`
	YAML string `json:"yaml"`
}

func main() {
	// Read initial pong data
	pongMd, _ := os.ReadFile("pong.md")
	pongYaml, _ := os.ReadFile("pong.yaml")

	// Create webview

	// Create webview
	debug := true
	w := webview.New(debug)
	defer w.Destroy()

	w.SetTitle("Project View & Logic Canvas")
	w.SetSize(1400, 900, 0)

	// Bind Project Data Fetcher
	w.Bind("getProjectData", func(name string) ProjectData {
		md, _ := os.ReadFile(name + ".md")
		yaml, _ := os.ReadFile(name + ".yaml")
		return ProjectData{
			Name: name,
			MD:   string(md),
			YAML: string(yaml),
		}
	})

	// Bind Project Loader
	w.Bind("loadProjectGame", func(name string) string {
		htmlFile := name + "_code.html"
		// Check if the html file exists
		if _, err := os.Stat(htmlFile); os.IsNotExist(err) {
			fmt.Printf("%s not found, generating...\n", htmlFile)
			// Assuming the generator script handles all projects based on naming convention
			// We might need to pass the project name to the script if it's not hardcoded
			cmd := exec.Command("python", name+"_gen.py") // Assuming name_gen.py exists
			// If it's always pong_gen.py but we want it to be generic:
			if name == "pong" {
				cmd = exec.Command("python", "pong_gen.py")
			} else {
				// For snake or breakout, check if their gen scripts exist
				genScript := name + "_gen.py"
				if _, err := os.Stat(genScript); err == nil {
					cmd = exec.Command("python", genScript)
				} else {
					return fmt.Sprintf("Error: Generation script %s not found", genScript)
				}
			}

			output, err := cmd.CombinedOutput()
			if err != nil {
				return fmt.Sprintf("Error generating %s: %v\nOutput: %s", name, err, string(output))
			}
			fmt.Println("Generation successful.")
		}

		// Read the generated html
		content, err := os.ReadFile(htmlFile)
		if err != nil {
			return fmt.Sprintf("Error reading %s: %v", htmlFile, err)
		}
		return string(content)
	})

	// Prepare HTML
	html := fmt.Sprintf(`
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Project & Logic View</title>
			<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>
			<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Fira+Code:wght@400&display=swap" rel="stylesheet">
			<style>
				:root {
					--bg: #0f172a;
					--panel-bg: rgba(30, 41, 59, 0.7);
					--text: #f8fafc;
					--text-dim: #94a3b8;
					--primary: #3b82f6;
					--secondary: #10b981;
					--border: rgba(255, 255, 255, 0.1);
					--accent: #8b5cf6;
				}

				body {
					font-family: 'Inter', sans-serif;
					background-color: var(--bg);
					color: var(--text);
					margin: 0;
					padding: 0;
					overflow: hidden;
					height: 100vh;
					display: flex;
					flex-direction: column;
				}

				nav {
					padding: 0.75rem 2rem;
					background: #1e293b;
					border-bottom: 1px solid var(--border);
					display: flex;
					align-items: center;
					gap: 1rem;
					z-index: 100;
				}

				.nav-brand {
					font-weight: 800;
					font-size: 1.1rem;
					color: var(--primary);
					margin-right: 1.5rem;
					letter-spacing: -0.025em;
				}

				.nav-item {
					cursor: pointer;
					padding: 0.5rem 1rem;
					border-radius: 6px;
					transition: all 0.2s;
					font-weight: 600;
					color: var(--text-dim);
				}

				.nav-item.active {
					background: var(--primary);
					color: white;
				}

				.project-selector {
					background: rgba(255, 255, 255, 0.05);
					border: 1px solid var(--border);
					color: var(--text);
					padding: 0.5rem;
					border-radius: 6px;
					font-weight: 600;
					outline: none;
					cursor: pointer;
				}

				.project-selector option {
					background: var(--bg);
				}

				.btn-run {
					margin-left: auto;
					background: var(--secondary);
					color: white;
					border: none;
					padding: 0.6rem 1.2rem;
					border-radius: 6px;
					font-weight: 800;
					cursor: pointer;
					display: flex;
					align-items: center;
					gap: 0.5rem;
					transition: transform 0.2s;
				}

				.btn-run:hover {
					transform: translateY(-2px);
					filter: brightness(1.1);
				}

				.content-view {
					flex-grow: 1;
					display: none;
					padding: 2rem;
					overflow: auto;
					position: relative;
				}

				.content-view.active {
					display: flex;
				}

				/* Game View Styles */
				#game-view {
					flex-direction: column;
					padding: 0;
					background: #000;
					overflow: hidden;
				}

				#game-frame {
					width: 100%;
					height: 100%;
					border: none;
					background: #0f172a;
				}

				.loading-overlay {
					position: absolute;
					top: 0; left: 0; right: 0; bottom: 0;
					background: rgba(15, 23, 42, 0.9);
					display: flex;
					flex-direction: column;
					align-items: center;
					justify-content: center;
					z-index: 200;
					gap: 1rem;
				}

				.spinner {
					width: 40px;
					height: 40px;
					border: 4px solid rgba(255,255,255,0.1);
					border-left-color: var(--primary);
					border-radius: 50%;
					animation: spin 1s linear infinite;
				}

				@keyframes spin {
					to { transform: rotate(360deg); }
				}

				/* Project View Styles */
				#project-view {
					flex-direction: column;
					gap: 2rem;
					align-items: center;
				}

				.preview-card {
					background: var(--panel-bg);
					backdrop-filter: blur(8px);
					border-radius: 12px;
					border: 1px solid var(--border);
					width: 100%%;
					max-width: 1000px;
					padding: 1.5rem;
					box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
				}

				.preview-card h2 {
					margin-top: 0;
					font-size: 1.25rem;
					color: var(--primary);
					margin-bottom: 1rem;
					display: flex;
					align-items: center;
					gap: 0.5rem;
				}

				.code-preview {
					background: #000;
					border-radius: 8px;
					padding: 1rem;
					font-family: 'Fira Code', monospace;
					font-size: 0.85rem;
					height: 12rem; /* Roughly 10 rows */
					overflow-y: auto;
					white-space: pre;
					border: 1px solid #334155;
					position: relative;
				}

				/* Canvas View Styles */
				#canvas-view {
					padding: 0;
					background: radial-gradient(circle at 50%% 50%%, #1e293b 0%%, #0f172a 100%%);
					overflow: hidden;
				}

				#canvas-container {
					width: 100%%;
					height: 100%%;
					position: relative;
					overflow: hidden;
					cursor: crosshair;
				}

				#canvas-inner {
					position: absolute;
					width: 5000px;
					height: 5000px;
					transform-origin: 0 0;
					will-change: transform;
				}

				.node {
					position: absolute;
					padding: 1rem;
					border-radius: 8px;
					border: 2px solid transparent;
					min-width: 150px;
					box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
					cursor: grab;
					z-index: 10;
				}

				.node:active {
					cursor: grabbing;
				}

				.node-table {
					background: #1e3a8a;
					border-color: #3b82f6;
				}

				.node-function {
					background: #064e3b;
					border-color: #10b981;
				}

				.node h3 {
					margin: 0;
					font-size: 0.9rem;
					text-align: center;
					border-bottom: 1px solid rgba(255, 255, 255, 0.2);
					padding-bottom: 0.5rem;
					margin-bottom: 0.5rem;
					pointer-events: none;
				}

				.node .details {
					font-size: 0.75rem;
					font-family: 'Fira Code', monospace;
					color: rgba(255, 255, 255, 0.8);
					pointer-events: none;
				}

				svg#connections {
					position: absolute;
					top: 0;
					left: 0;
					width: 100%%;
					height: 100%%;
					pointer-events: none;
					z-index: 5;
				}

				path.connector {
					fill: none;
					stroke: rgba(148, 163, 184, 0.4);
					stroke-width: 2;
					marker-end: url(#arrowhead);
				}

				.zoom-controls {
					position: absolute;
					bottom: 20px;
					right: 20px;
					background: var(--panel-bg);
					backdrop-filter: blur(8px);
					padding: 0.5rem;
					border-radius: 8px;
					border: 1px solid var(--border);
					display: flex;
					gap: 0.5rem;
					z-index: 1000;
				}

				.zoom-btn {
					padding: 0.5rem;
					background: rgba(255, 255, 255, 0.1);
					border: none;
					color: white;
					border-radius: 4px;
					cursor: pointer;
					font-weight: bold;
				}

				.zoom-btn:hover {
					background: var(--primary);
				}

				::-webkit-scrollbar { width: 8px; height: 8px; }
				::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); }
				::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
			</style>
		</head>
		<body>
			<nav>
				<div class="nav-brand">LogicCanvas</div>
				<select id="project-select" class="project-selector" onchange="changeProject(this.value)">
					<option value="pong">Pong</option>
					<option value="snake">Snake</option>
					<option value="breakout">Breakout</option>
				</select>
				<div class="nav-item active" onclick="showView('project')">Project View</div>
				<div class="nav-item" onclick="showView('canvas')">Canvas View</div>
				<button class="btn-run" onclick="runCurrentProject()">
					<span>▶</span> Run Project
				</button>
			</nav>

			<div id="project-view" class="content-view active">
				<div class="preview-card">
					<h2 id="md-title">📄 pong.md</h2>
					<div class="code-preview" id="md-preview"></div>
				</div>
				<div class="preview-card">
					<h2 id="yaml-title">⚙️ pong.yaml</h2>
					<div class="code-preview" id="yaml-preview"></div>
				</div>
			</div>

			<div id="canvas-view" class="content-view">
				<div id="canvas-container">
					<div id="canvas-inner">
						<svg id="connections">
							<defs>
								<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
									<polygon points="0 0, 10 3.5, 0 7" fill="rgba(148, 163, 184, 0.8)" />
								</marker>
							</defs>
						</svg>
					</div>
					<div class="zoom-controls">
						<button class="zoom-btn" onclick="zoom(0.1)">+</button>
						<button class="zoom-btn" onclick="resetZoom()">1:1</button>
						<button class="zoom-btn" onclick="zoom(-0.1)">-</button>
						<div id="zoom-level" style="font-size: 0.8rem; display: flex; align-items: center; margin-left: 0.5rem;">100%%</div>
					</div>
				</div>
			</div>

			<div id="game-view" class="content-view">
				<div id="game-loading" class="loading-overlay" style="display: none;">
					<div class="spinner"></div>
					<div id="loading-text">Generating & Loading Project...</div>
				</div>
				<iframe id="game-frame"></iframe>
			</div>

			<script>
				let currentProject = 'pong';
				let projectData = {
					pong: { yaml: %q, md: %q }
				};

				async function changeProject(name) {
					currentProject = name;
					if (!projectData[name]) {
						const data = await window.getProjectData(name);
						projectData[name] = { yaml: data.yaml, md: data.md };
					}
					
					// Update UI
					document.getElementById('md-title').textContent = '📄 ' + name + '.md';
					document.getElementById('yaml-title').textContent = '⚙️ ' + name + '.yaml';
					document.getElementById('md-preview').textContent = projectData[name].md;
					document.getElementById('yaml-preview').textContent = projectData[name].yaml;
					
					// Reset canvas so it re-renders
					canvasData = null;
					const inner = document.getElementById('canvas-inner');
					Array.from(inner.children).forEach(c => {
						if (c.id !== 'connections') c.remove();
					});
					
					// Reset game frame
					const iframe = document.getElementById('game-frame');
					iframe.srcdoc = '';

					if (document.getElementById('canvas-view').classList.contains('active')) {
						renderCanvas();
					}
				}

				function showView(viewId) {
					document.querySelectorAll('.content-view').forEach(v => v.classList.remove('active'));
					document.querySelectorAll('.nav-item').forEach(v => v.classList.remove('active'));
					
					const view = document.getElementById(viewId + '-view');
					if (view) view.classList.add('active');
					
					const navItem = Array.from(document.querySelectorAll('.nav-item')).find(n => n.textContent.toLowerCase().includes(viewId));
					if (navItem) navItem.classList.add('active');

					if (viewId === 'canvas') {
						renderCanvas();
					}
				}

				async function runCurrentProject() {
					showView('game');
					const loading = document.getElementById('game-loading');
					const iframe = document.getElementById('game-frame');
					const loadingText = document.getElementById('loading-text');

					if (iframe.srcdoc && iframe.dataset.project === currentProject) {
						return; 
					}

					loading.style.display = 'flex';
					loadingText.textContent = 'Generating & Loading ' + currentProject.toUpperCase() + '...';
					
					try {
						const html = await window.loadProjectGame(currentProject);
						if (html.startsWith('Error')) {
							alert(html);
						} else {
							iframe.srcdoc = html;
							iframe.dataset.project = currentProject;
						}
					} catch (e) {
						alert('Failed to load project: ' + e);
					} finally {
						loading.style.display = 'none';
					}
				}

				// Initialize Project View
				document.getElementById('md-preview').textContent = projectData.pong.md;
				document.getElementById('yaml-preview').textContent = projectData.pong.yaml;

				// Canvas State
				let canvasData = null;
				let transform = { x: 50, y: 50, scale: 1.0 };
				let isPanning = false;
				let activeNode = null;
				let dragStart = { x: 0, y: 0 };
				let nodeOffset = { x: 0, y: 0 };

				const inner = document.getElementById('canvas-inner');
				const container = document.getElementById('canvas-container');

				function applyTransform() {
					inner.style.transform = "translate(" + transform.x + "px, " + transform.y + "px) scale(" + transform.scale + ")";
					document.getElementById('zoom-level').textContent = Math.round(transform.scale * 100) + "%%";
				}

				function zoom(delta) {
					const oldScale = transform.scale;
					transform.scale = Math.max(0.1, Math.min(5, transform.scale + delta));
					
					// Zoom toward center of screen
					const rect = container.getBoundingClientRect();
					const centerX = rect.width / 2;
					const centerY = rect.height / 2;
					
					const worldX = (centerX - transform.x) / oldScale;
					const worldY = (centerY - transform.y) / oldScale;
					
					transform.x = centerX - worldX * transform.scale;
					transform.y = centerY - worldY * transform.scale;
					
					applyTransform();
				}

				function resetZoom() {
					transform = { x: 50, y: 50, scale: 1.0 };
					applyTransform();
				}

				function renderCanvas() {
					if (canvasData) return;

					try {
						canvasData = jsyaml.load(projectData[currentProject].yaml);
					} catch (e) {
						return;
					}

					const tableNodes = {};
					const functionNodes = {};

					// Layout params
					const marginX = 100;
					const marginY = 50;
					const spacingX = 400;
					const spacingY = 200;

					// Create Table Nodes
					let i = 0;
					for (const tableName in canvasData.tables) {
						const table = canvasData.tables[tableName];
						const node = createNode(tableName, 'table', table.columns);
						node.style.left = marginX + 'px';
						node.style.top = (marginY + i * spacingY) + 'px';
						inner.appendChild(node);
						tableNodes[tableName] = node;
						i++;
					}

					// Create Function Nodes
					i = 0;
					for (const funcName in canvasData.functions) {
						const func = canvasData.functions[funcName];
						const node = createNode(funcName, 'function', { 
							in: func.inputs?.join(', ') || 'none',
							out: func.outputs?.join(', ') || 'none'
						});
						node.style.left = (marginX + spacingX) + 'px';
						node.style.top = (marginY + i * (spacingY * 0.8)) + 'px';
						inner.appendChild(node);
						functionNodes[funcName] = node;
						i++;
					}

					updateConnections(canvasData, tableNodes, functionNodes);
					applyTransform();
				}

				function createNode(name, type, info) {
					const div = document.createElement('div');
					div.className = 'node node-' + type;
					div.id = 'node-' + name;
					
					const h3 = document.createElement('h3');
					h3.textContent = name;
					div.appendChild(h3);

					const details = document.createElement('div');
					details.className = 'details';
					for (const key in info) {
						const p = document.createElement('div');
						p.textContent = key + ': ' + info[key];
						details.appendChild(p);
					}
					div.appendChild(details);
					return div;
				}

				function updateConnections(data, tableNodes, functionNodes) {
					const svg = document.getElementById('connections');
					Array.from(svg.querySelectorAll('path.connector')).forEach(p => p.remove());

					for (const funcName in data.functions) {
						const func = data.functions[funcName];
						const funcEl = functionNodes[funcName];

						if (func.inputs) {
							func.inputs.forEach(tableName => {
								const tableEl = tableNodes[tableName];
								if (tableEl && funcEl) drawArrow(tableEl, funcEl, 'input');
							});
						}

						if (func.outputs) {
							func.outputs.forEach(tableName => {
								const tableEl = tableNodes[tableName];
								if (tableEl && funcEl) drawArrow(funcEl, tableEl, 'output');
							});
						}
					}
				}

				function drawArrow(fromEl, toEl, type) {
					const svg = document.getElementById('connections');
					const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
					path.setAttribute('class', 'connector ' + type);
					svg.appendChild(path);

					function updatePath() {
						const startX = fromEl.offsetLeft + fromEl.offsetWidth;
						const startY = fromEl.offsetTop + fromEl.offsetHeight / 2;
						const endX = toEl.offsetLeft;
						const endY = toEl.offsetTop + toEl.offsetHeight / 2;
						const cp1x = startX + (endX - startX) / 2;
						const cp2x = startX + (endX - startX) / 2;
						const d = 'M ' + startX + ' ' + startY + ' C ' + cp1x + ' ' + startY + ' ' + cp2x + ' ' + endY + ' ' + endX + ' ' + endY;
						path.setAttribute('d', d);
					}

					updatePath();
					fromEl.addEventListener('move', updatePath);
					toEl.addEventListener('move', updatePath);
				}

				// Event Handling
				container.addEventListener('mousedown', e => {
					const node = e.target.closest('.node');
					if (node) {
						activeNode = node;
						nodeOffset.x = (e.clientX - container.getBoundingClientRect().left) / transform.scale - node.offsetLeft;
						nodeOffset.y = (e.clientY - container.getBoundingClientRect().top) / transform.scale - node.offsetTop;
						node.style.zIndex = 1000;
					} else {
						isPanning = true;
						dragStart.x = e.clientX - transform.x;
						dragStart.y = e.clientY - transform.y;
					}
				});

				window.addEventListener('mousemove', e => {
					if (activeNode) {
						const containerRect = container.getBoundingClientRect();
						let x = (e.clientX - containerRect.left) / transform.scale - nodeOffset.x;
						let y = (e.clientY - containerRect.top) / transform.scale - nodeOffset.y;
						activeNode.style.left = x + 'px';
						activeNode.style.top = y + 'px';
						activeNode.dispatchEvent(new CustomEvent('move'));
					} else if (isPanning) {
						transform.x = e.clientX - dragStart.x;
						transform.y = e.clientY - dragStart.y;
						applyTransform();
					}
				});

				window.addEventListener('mouseup', () => {
					if (activeNode) activeNode.style.zIndex = 10;
					activeNode = null;
					isPanning = false;
				});

				container.addEventListener('wheel', e => {
					e.preventDefault();
					const delta = e.deltaY > 0 ? -0.1 : 0.1;
					
					// Zoom relative to mouse position
					const rect = container.getBoundingClientRect();
					const mouseX = e.clientX - rect.left;
					const mouseY = e.clientY - rect.top;
					
					const oldScale = transform.scale;
					transform.scale = Math.max(0.1, Math.min(5, transform.scale + delta));
					
					const worldX = (mouseX - transform.x) / oldScale;
					const worldY = (mouseY - transform.y) / oldScale;
					
					transform.x = mouseX - worldX * transform.scale;
					transform.y = mouseY - worldY * transform.scale;
					
					applyTransform();
				}, { passive: false });

			</script>
		</body>
		</html>
	`, string(pongYaml), string(pongMd))

	w.SetHtml(html)
	w.Run()
}
