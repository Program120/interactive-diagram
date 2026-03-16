---
name: interactive-diagram
description: |
  Generate interactive, draggable HTML diagrams — flowcharts, architecture diagrams, mind maps, and sequence diagrams — as standalone HTML files with no external dependencies.
  Use this skill whenever the user asks to draw, visualize, or create any kind of diagram, chart, flowchart, architecture diagram, mind map, sequence diagram, or visual representation of a system, process, or concept.
  Trigger keywords: 画图, 流程图, 架构图, 思维导图, 时序图, diagram, flowchart, architecture, mind map, sequence diagram, 画一个, 可视化, visualize, 拓扑图, 关系图, draw, 图解, 示意图.
  Also trigger when users describe processes, architectures, or relationships that would benefit from visual representation, even if they don't explicitly say "draw" — for example "show me how these services connect" or "这个流程是怎样的".
---

# Interactive Diagram Generator

You generate standalone, interactive HTML files that render beautiful, draggable diagrams directly in the browser. No CDN, no npm, no external dependencies — everything is self-contained in a single HTML file.

## When to Use

- User asks to draw/create/visualize any diagram
- User describes a process, architecture, or relationship that benefits from visualization
- User says things like "画个图", "画流程图", "show me the flow", "架构图", "思维导图"

## Supported Diagram Types

### 1. Flowchart (流程图)
- Nodes: rounded rectangles for processes, diamonds for decisions, ovals for start/end
- Layout: top-to-bottom or left-to-right
- Connections: arrows with optional labels (Yes/No for decisions)

### 2. Architecture Diagram (架构图)
- Nodes: rectangles with icons/labels representing services, databases, queues, etc.
- Groups: dashed-border containers for grouping related components (e.g., "Backend", "Frontend")
- Connections: lines with protocol labels (HTTP, gRPC, WebSocket, etc.)

### 3. Mind Map (思维导图)
- Central node radiating outward
- Hierarchical branches with decreasing size
- Color-coded branches for different categories

### 4. Sequence Diagram (时序图)
- Vertical lifelines for participants
- Horizontal arrows for messages between participants
- Activation boxes showing processing time

## Output Requirements

Generate a **single HTML file** that:
1. Opens directly in any modern browser
2. Has zero external dependencies (all CSS/JS inline)
3. Supports node dragging (mousedown/mousemove/mouseup + touch events)
4. Auto-updates connection lines when nodes move
5. Has a clean, modern UI with subtle shadows, rounded corners, and a professional color palette

## HTML Generation Template

Use the template engine script at `scripts/diagram_engine.py` to understand the core patterns for each diagram type. But you can also generate the HTML directly — the key is following these patterns:

### Core Architecture

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Diagram Title]</title>
  <style>
    /* --- Reset & Base --- */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f0f2f5;
      overflow: hidden;
    }

    /* --- Toolbar --- */
    .toolbar {
      position: fixed; top: 0; left: 0; right: 0; height: 48px;
      background: #fff; border-bottom: 1px solid #e8e8e8;
      display: flex; align-items: center; padding: 0 16px;
      z-index: 1000; gap: 8px;
    }
    .toolbar h1 { font-size: 16px; font-weight: 600; color: #1a1a1a; }
    .toolbar-spacer { flex: 1; }
    .toolbar button {
      padding: 6px 14px; border: 1px solid #d9d9d9; border-radius: 6px;
      background: #fff; cursor: pointer; font-size: 13px; color: #333;
      transition: all 0.2s;
    }
    .toolbar button:hover { border-color: #4096ff; color: #4096ff; }

    /* --- Canvas --- */
    .canvas {
      position: absolute; top: 48px; left: 0; right: 0; bottom: 0;
      overflow: hidden; cursor: grab;
    }
    .canvas.dragging { cursor: grabbing; }
    .canvas-inner {
      position: absolute; transform-origin: 0 0;
      width: 5000px; height: 5000px;
    }

    /* --- SVG layer for connections --- */
    .connections {
      position: absolute; top: 0; left: 0;
      width: 100%; height: 100%;
      pointer-events: none;
    }
    .connections line, .connections path {
      stroke: #8c8c8c; stroke-width: 2; fill: none;
    }
    .connections .arrow { fill: #8c8c8c; }
    .connection-label {
      font-size: 12px; fill: #666; text-anchor: middle;
    }

    /* --- Node base --- */
    .node {
      position: absolute; cursor: move; user-select: none;
      transition: box-shadow 0.2s;
    }
    .node:hover { z-index: 100; }
    .node.dragging {
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
      z-index: 101;
    }
  </style>
</head>
<body>
  <div class="toolbar">
    <h1>📊 [Title]</h1>
    <div class="toolbar-spacer"></div>
    <button onclick="resetView()">重置视图</button>
    <button onclick="exportPNG()">导出 PNG</button>
    <button onclick="exportSVG()">导出 SVG</button>
    <button onclick="exportJSON()">导出 JSON</button>
  </div>

  <div class="canvas" id="canvas">
    <div class="canvas-inner" id="canvasInner">
      <svg class="connections" id="connections"></svg>
      <!-- Nodes go here -->
    </div>
  </div>

  <script>
    // === Diagram Data ===
    const nodes = [/* node definitions */];
    const edges = [/* edge definitions */];

    // === Drag System ===
    // ... (see implementation patterns below)

    // === Pan & Zoom ===
    // ... (see implementation patterns below)

    // === Connection Rendering ===
    // ... (see implementation patterns below)

    // === Export Functions ===
    // ... (see implementation patterns below)
  </script>
</body>
</html>
```

### Drag System Implementation

The drag system must handle both mouse and touch events:

```javascript
let dragState = null;

function initDrag(nodeEl, nodeId) {
  const onStart = (e) => {
    e.preventDefault();
    const pos = getEventPos(e);
    const rect = nodeEl.getBoundingClientRect();
    dragState = {
      node: nodeEl, id: nodeId,
      offsetX: pos.x - rect.left,
      offsetY: pos.y - rect.top
    };
    nodeEl.classList.add('dragging');
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onEnd);
    document.addEventListener('touchmove', onMove, { passive: false });
    document.addEventListener('touchend', onEnd);
  };

  const onMove = (e) => {
    if (!dragState) return;
    e.preventDefault();
    const pos = getEventPos(e);
    const canvasRect = canvas.getBoundingClientRect();
    const x = (pos.x - canvasRect.left - dragState.offsetX) / scale - panX / scale;
    const y = (pos.y - canvasRect.top - dragState.offsetY) / scale - panY / scale;
    dragState.node.style.left = x + 'px';
    dragState.node.style.top = y + 'px';
    // Update the node data
    const nd = nodes.find(n => n.id === dragState.id);
    if (nd) { nd.x = x; nd.y = y; }
    updateConnections();
  };

  const onEnd = () => {
    if (dragState) dragState.node.classList.remove('dragging');
    dragState = null;
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onEnd);
    document.removeEventListener('touchmove', onMove);
    document.removeEventListener('touchend', onEnd);
  };

  nodeEl.addEventListener('mousedown', onStart);
  nodeEl.addEventListener('touchstart', onStart, { passive: false });
}

function getEventPos(e) {
  if (e.touches) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
  return { x: e.clientX, y: e.clientY };
}
```

### Pan & Zoom

```javascript
let scale = 1, panX = 0, panY = 0;
const canvasInner = document.getElementById('canvasInner');
const canvas = document.getElementById('canvas');

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const delta = e.deltaY > 0 ? 0.9 : 1.1;
  scale = Math.max(0.3, Math.min(3, scale * delta));
  applyTransform();
});

let isPanning = false, panStart = {};
canvas.addEventListener('mousedown', (e) => {
  if (e.target === canvas || e.target === canvasInner) {
    isPanning = true;
    panStart = { x: e.clientX - panX, y: e.clientY - panY };
    canvas.classList.add('dragging');
  }
});
document.addEventListener('mousemove', (e) => {
  if (!isPanning) return;
  panX = e.clientX - panStart.x;
  panY = e.clientY - panStart.y;
  applyTransform();
});
document.addEventListener('mouseup', () => {
  isPanning = false;
  canvas.classList.remove('dragging');
});

function applyTransform() {
  canvasInner.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
}
function resetView() { scale = 1; panX = 0; panY = 0; applyTransform(); }
```

### Connection Rendering

Use SVG for connections. Recalculate on every node move:

```javascript
function updateConnections() {
  const svg = document.getElementById('connections');
  svg.innerHTML = '';

  edges.forEach(edge => {
    const from = nodes.find(n => n.id === edge.from);
    const to = nodes.find(n => n.id === edge.to);
    if (!from || !to) return;

    const fromEl = document.getElementById('node-' + from.id);
    const toEl = document.getElementById('node-' + to.id);
    if (!fromEl || !toEl) return;

    const x1 = from.x + fromEl.offsetWidth / 2;
    const y1 = from.y + fromEl.offsetHeight;
    const x2 = to.x + toEl.offsetWidth / 2;
    const y2 = to.y;

    // Bezier curve for smooth connections
    const midY = (y1 + y2) / 2;
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`);
    path.setAttribute('stroke', edge.color || '#8c8c8c');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    path.setAttribute('marker-end', 'url(#arrowhead)');
    svg.appendChild(path);

    // Label
    if (edge.label) {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', (x1 + x2) / 2);
      text.setAttribute('y', midY - 8);
      text.setAttribute('class', 'connection-label');
      text.textContent = edge.label;
      svg.appendChild(text);
    }
  });
}
```

### Export Functions

```javascript
function exportPNG() {
  // Use canvas API to render the diagram area
  const area = document.getElementById('canvasInner');
  const rect = getContentBounds();
  const cvs = document.createElement('canvas');
  const dpr = window.devicePixelRatio || 2;
  cvs.width = rect.width * dpr;
  cvs.height = rect.height * dpr;
  const ctx = cvs.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.fillStyle = '#f0f2f5';
  ctx.fillRect(0, 0, rect.width, rect.height);

  // Serialize to SVG foreignObject then draw
  const data = new XMLSerializer().serializeToString(area);
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="${rect.width}" height="${rect.height}">
    <foreignObject width="100%" height="100%">
      <div xmlns="http://www.w3.org/1999/xhtml">${data}</div>
    </foreignObject>
  </svg>`;
  const img = new Image();
  img.onload = () => {
    ctx.drawImage(img, -rect.x, -rect.y);
    const link = document.createElement('a');
    link.download = 'diagram.png';
    link.href = cvs.toDataURL('image/png');
    link.click();
  };
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr);
}

function exportSVG() {
  const svg = document.getElementById('connections').cloneNode(true);
  // Add node representations as SVG elements
  const svgStr = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([svgStr], { type: 'image/svg+xml' });
  const link = document.createElement('a');
  link.download = 'diagram.svg';
  link.href = URL.createObjectURL(blob);
  link.click();
}

function exportJSON() {
  const data = JSON.stringify({ nodes, edges }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const link = document.createElement('a');
  link.download = 'diagram.json';
  link.href = URL.createObjectURL(blob);
  link.click();
}

function getContentBounds() {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  nodes.forEach(n => {
    const el = document.getElementById('node-' + n.id);
    if (!el) return;
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + el.offsetWidth);
    maxY = Math.max(maxY, n.y + el.offsetHeight);
  });
  const pad = 40;
  return { x: minX - pad, y: minY - pad, width: maxX - minX + pad * 2, height: maxY - minY + pad * 2 };
}
```

## Design System

### Color Palette

Use a modern, professional palette. Assign colors by role:

| Role | Color | Use For |
|------|-------|---------|
| Primary | `#4096ff` | Primary actions, active states |
| Success | `#52c41a` | Success nodes, start nodes |
| Warning | `#faad14` | Warning, decision nodes |
| Error | `#ff4d4f` | Error nodes, end nodes |
| Purple | `#722ed1` | Service/API nodes |
| Cyan | `#13c2c2` | Database/storage nodes |
| Background | `#f0f2f5` | Canvas background |
| Card | `#ffffff` | Node background |
| Text | `#1a1a1a` | Primary text |
| Secondary | `#8c8c8c` | Secondary text, lines |

### Node Styles by Type

**Process Node** (flowchart):
```css
.node-process {
  background: #fff; border: 2px solid #4096ff; border-radius: 8px;
  padding: 12px 24px; font-size: 14px; color: #1a1a1a;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
```

**Decision Node** (flowchart):
```css
.node-decision {
  background: #fff7e6; border: 2px solid #faad14;
  transform: rotate(45deg); /* container rotated, inner text counter-rotated */
}
.node-decision .inner { transform: rotate(-45deg); }
```

**Service Node** (architecture):
```css
.node-service {
  background: #fff; border: 2px solid #722ed1; border-radius: 12px;
  padding: 16px; min-width: 120px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.node-service .icon { font-size: 28px; margin-bottom: 8px; }
.node-service .label { font-size: 13px; font-weight: 500; }
```

**Mind Map Node**:
```css
.node-central {
  background: linear-gradient(135deg, #4096ff, #722ed1);
  color: #fff; border-radius: 50%; width: 120px; height: 120px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 600;
}
.node-branch {
  background: #fff; border-left: 4px solid var(--branch-color);
  border-radius: 8px; padding: 10px 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
```

## Step-by-Step Generation Process

When the user asks for a diagram:

1. **Identify diagram type** from context (flowchart, architecture, mind map, sequence)
2. **Extract nodes and relationships** from the user's description
3. **Calculate initial layout positions** — use simple algorithms:
   - Flowchart: top-to-bottom with even spacing (~150px vertical, ~200px horizontal)
   - Architecture: grid-based with groups
   - Mind map: radial from center
   - Sequence: left-to-right lifelines with top-to-bottom messages
4. **Generate the complete HTML file** following the template above
5. **Write the file** to the current directory (e.g., `diagram.html`)
6. **Open in browser**: `open diagram.html` (macOS) or `xdg-open diagram.html` (Linux)

## Important Notes

- Every diagram must be fully self-contained — **zero external dependencies**
- All CSS and JS must be inline in the HTML file
- Support both mouse and touch events for dragging
- Include pan (drag canvas) and zoom (scroll wheel) functionality
- The SVG connection layer must update in real-time as nodes are dragged
- Include the arrowhead marker definition in the SVG defs
- Use emoji as icons in architecture diagrams (🗄️ database, 🌐 web, ⚙️ service, etc.) to avoid needing icon fonts
- Always include a toolbar with Reset View, Export PNG, Export SVG, and Export JSON buttons
- File name should be descriptive: `user_auth_flow.html`, `system_architecture.html`, etc.
- After generating, always open the file in the browser so the user can see it immediately
