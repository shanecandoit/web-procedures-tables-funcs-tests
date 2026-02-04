let currentProject = 'pong';
let projectData = {};

async function init() {
    console.log('Initializing application...');
    // Load initial project data
    await changeProject('pong');
}

async function changeProject(name) {
    console.log('Changing project to:', name);
    currentProject = name;
    if (!projectData[name]) {
        console.log('Loading project data for:', name);
        try {
            const data = await window.getProjectData(name);
            projectData[name] = { yaml: data.yaml, md: data.md };
            console.log('Loaded:', name, 'yaml:', data.yaml?.length, 'md:', data.md?.length);
        } catch (error) {
            console.error('Error loading project data:', error);
            return;
        }
    }
    
    // Update UI
    const mdTitle = document.getElementById('md-title');
    const yamlTitle = document.getElementById('yaml-title');
    const mdPreview = document.getElementById('md-preview');
    const yamlPreview = document.getElementById('yaml-preview');

    if (mdTitle) mdTitle.textContent = '📄 ' + name + '.md';
    if (yamlTitle) yamlTitle.textContent = '⚙️ ' + name + '.yaml';
    if (mdPreview) mdPreview.textContent = projectData[name].md;
    if (yamlPreview) yamlPreview.textContent = projectData[name].yaml;
    
    console.log('Updated previews for:', name);
    
    // Reset canvas so it re-renders
    canvasData = null;
    const inner = document.getElementById('canvas-inner');
    if (inner) {
        Array.from(inner.children).forEach(c => {
            if (c.id !== 'connections') c.remove();
        });
    }
    
    // Reset game frame
    const iframe = document.getElementById('game-frame');
    if (iframe) {
        iframe.srcdoc = '';
    }

    if (document.getElementById('canvas-view').classList.contains('active')) {
        await renderCanvas();
    }
}

async function showView(viewId) {
    document.querySelectorAll('.content-view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(v => v.classList.remove('active'));
    
    const view = document.getElementById(viewId + '-view');
    if (view) view.classList.add('active');
    
    const navItem = Array.from(document.querySelectorAll('.nav-item')).find(n => n.textContent.toLowerCase().includes(viewId));
    if (navItem) navItem.classList.add('active');

    if (viewId === 'canvas') {
        await renderCanvas();
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

// Canvas State
let canvasData = null;
let transform = { x: 50, y: 50, scale: 1.0 };
let isPanning = false;
let activeNode = null;
let dragStart = { x: 0, y: 0 };
let nodeOffset = { x: 0, y: 0 };

function applyTransform() {
    const inner = document.getElementById('canvas-inner');
    if (!inner) return;
    inner.style.transform = "translate(" + transform.x + "px, " + transform.y + "px) scale(" + transform.scale + ")";
    const zoomLevel = document.getElementById('zoom-level');
    if (zoomLevel) zoomLevel.textContent = Math.round(transform.scale * 100) + "%";
}

function zoom(delta) {
    const container = document.getElementById('canvas-container');
    if (!container) return;
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

async function renderCanvas() {
    if (canvasData) return;

    const inner = document.getElementById('canvas-inner');
    if (!inner) return;

    // Ensure project data is loaded
    if (!projectData[currentProject]) {
        const data = await window.getProjectData(currentProject);
        projectData[currentProject] = { yaml: data.yaml, md: data.md };
    }

    try {
        canvasData = jsyaml.load(projectData[currentProject].yaml);
    } catch (e) {
        console.error('Failed to parse YAML:', e);
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
    if (!svg) return;
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
    if (!svg) return;
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
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('canvas-container');
    if (!container) return;

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

    init();
});
