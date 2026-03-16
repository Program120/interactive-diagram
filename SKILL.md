---
name: interactive-diagram
description: |
  Generate interactive, draggable diagrams with REAL-TIME incremental rendering via SSE.
  Supports flowcharts, architecture diagrams, mind maps, and sequence diagrams.
  Nodes appear one by one as the agent generates them — zero wait time.
  Use this skill whenever the user asks to draw, visualize, or create any kind of diagram.
  Trigger keywords: 画图, 流程图, 架构图, 思维导图, 时序图, diagram, flowchart, architecture,
  mind map, sequence diagram, 画一个, 可视化, visualize, 拓扑图, 关系图, draw, 图解, 示意图.
  Also trigger when users describe processes, architectures, or relationships that would benefit
  from visual representation, even if they don't explicitly say "draw".
---

# Interactive Diagram — Real-Time Incremental Rendering

This skill generates interactive diagrams using a **lightweight SSE server** and a **pre-built HTML renderer**.
Instead of generating entire HTML files, the agent sends tiny JSON commands via `curl`.
Each node and edge appears in the browser **in real-time** as the agent generates it.

## Architecture

```
Agent sends curl commands (~30-50 tokens each)
  → Python SSE Server (scripts/server.py)
    → Server-Sent Events push to browser
      → template.html renders incrementally with Dagre auto-layout
```

## Quick Start Workflow

### Step 1: Start the server (if not running)

Check if server is already running:
```bash
curl -s http://127.0.0.1:6100/status 2>/dev/null || python3 ~/.claude/skills/interactive-diagram/scripts/server.py &
```

Wait briefly for server startup, then verify:
```bash
sleep 1 && curl -s http://127.0.0.1:6100/status
```

### Step 2: Initialize the diagram

```bash
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"init","title":"图表标题","direction":"TB"}'
```

Direction options: `TB` (top-bottom), `LR` (left-right), `BT` (bottom-top), `RL` (right-left)

### Step 3: Add nodes one by one

```bash
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"n1","label":"开始","type":"terminal"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"n2","label":"处理数据","type":"process"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"n3","label":"是否成功?","type":"decision"}'
```

### Step 4: Add edges one by one

```bash
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"n1","to":"n2"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"n2","to":"n3","label":"验证"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"n3","to":"n4","label":"是","color":"green"}'
```

### Step 5 (optional): Trigger manual layout

Nodes auto-layout as they're added, but you can force a re-layout:
```bash
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"layout"}'
```

## Node Types

| type | Appearance | Usage |
|------|-----------|-------|
| `terminal` | Green gradient oval | Start node |
| `terminal-end` | Red gradient oval | End node |
| `process` | Blue-bordered rounded rect | Processing step |
| `decision` | Yellow-bordered diamond | Branch/condition |
| `service` | Purple-bordered rounded rect | Microservice/API |
| `database` | Cyan-bordered rect with thick top | Database/storage |
| `success` | Green-bordered rect | Success state |
| `error` | Red-bordered rect | Error/failure state |
| `group` | Dashed border container | Grouping |

Service nodes support an `icon` field: `{"cmd":"node","id":"s1","label":"API Gateway","type":"service","icon":"🔀"}`

## Edge Options

| Field | Required | Description |
|-------|----------|-------------|
| `from` | Yes | Source node ID |
| `to` | Yes | Target node ID |
| `label` | No | Text label on the edge |
| `color` | No | `blue`, `green`, `red`, `purple`, `cyan`, `orange`, or hex color |

## All Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Clear and initialize | `{"cmd":"init","title":"My Diagram","direction":"TB"}` |
| `node` | Add/update a node | `{"cmd":"node","id":"n1","label":"Step 1","type":"process"}` |
| `edge` | Add an edge | `{"cmd":"edge","from":"n1","to":"n2","label":"next"}` |
| `layout` | Force re-layout | `{"cmd":"layout"}` |
| `clear` | Clear all nodes/edges | `{"cmd":"clear"}` |
| `title` | Change title | `{"cmd":"title","text":"New Title"}` |
| `remove` | Remove a node | `{"cmd":"remove","id":"n1"}` |
| `batch` | Add multiple at once | `{"cmd":"batch","nodes":[...],"edges":[...]}` |
| `export` | Trigger export | `{"cmd":"export","format":"png"}` |

## CRITICAL RULES for the Agent

1. **ALWAYS start the server first.** Check with `curl -s 127.0.0.1:6100/status` before sending commands.
2. **Send nodes and edges INDIVIDUALLY** — one curl per node, one curl per edge. This creates the real-time incremental effect.
3. **Keep commands minimal** — only include required fields. Don't add unnecessary whitespace in JSON.
4. **Use descriptive IDs** — like `start`, `login`, `validate` instead of `n1`, `n2`, `n3`.
5. **Auto-layout handles positioning** — do NOT specify `x` or `y` coordinates. Dagre calculates optimal positions.
6. **Send init first** — always start with an `init` command to clear previous state and set the title.
7. **Add all nodes before edges** — this produces better layout results. Send all node commands first, then all edge commands, then optionally a `layout` command.

## Token Efficiency

Each curl command costs ~30-50 tokens. A 10-node flowchart uses ~500 tokens total.
This is 90% less than generating a full HTML file (~4000+ tokens).

## Fallback

If the server cannot start (e.g., port blocked, Python unavailable), fall back to generating
a standalone HTML file directly. Use the `batch` command format as a reference for the data structure,
and generate a complete HTML file with inline Dagre layout, CSS, and JS.

## Example: Complete Login Flow

```bash
# Start server
curl -s http://127.0.0.1:6100/status 2>/dev/null || python3 ~/.claude/skills/interactive-diagram/scripts/server.py &
sleep 1

# Initialize
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"init","title":"用户登录流程","direction":"TB"}'

# Add nodes
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"start","label":"开始","type":"terminal"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"input","label":"输入用户名密码","type":"process"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"validate","label":"验证信息","type":"process"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"check","label":"是否正确?","type":"decision"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"ok","label":"登录成功","type":"success"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"fail","label":"显示错误","type":"error"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"retry","label":"重试次数超限?","type":"decision"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"lock","label":"账户锁定","type":"error"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"end","label":"结束","type":"terminal-end"}'

# Add edges
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"start","to":"input"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"input","to":"validate"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"validate","to":"check"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"check","to":"ok","label":"是","color":"green"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"check","to":"fail","label":"否","color":"red"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"fail","to":"retry"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"retry","to":"input","label":"否"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"retry","to":"lock","label":"是","color":"red"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"ok","to":"end"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"lock","to":"end"}'
```
