<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill" />
  <img src="https://img.shields.io/badge/Zero-Dependencies-success?style=for-the-badge" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/AntV_X6-Interactive-orange?style=for-the-badge" alt="AntV X6" />
</p>

<h1 align="center">Interactive Diagram</h1>

<p align="center">
  <strong>Generate interactive diagrams with real-time incremental rendering via SSE — nodes appear one by one as the agent generates them.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#supported-diagram-types">Diagram Types</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#server-side-export">Export</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Features

- **Real-Time Incremental Rendering** — Nodes and edges appear one by one via SSE as the agent generates them
- **AntV X6 Engine** — Professional diagram editor powered by X6 v2 with Dagre auto-layout
- **Interactive Editing** — Drag nodes, double-click to edit labels, right-click context menu, connect ports
- **Multi-Session** — Multiple diagrams in parallel via `?s=session_name` URL parameter
- **Page Refresh Recovery** — Server stores all commands; refreshing replays full state
- **Server-Side Export** — Export PNG, SVG, JSON, Draw.io files to disk via curl commands
- **Browser Export** — PNG, SVG, JSON, Draw.io XML download or copy to clipboard from toolbar
- **Smooth Zoom** — Mouse wheel / trackpad zoom centered on cursor
- **Undo/Redo** — Full history support with Ctrl/Cmd+Z
- **Zero Python Dependencies** — Server uses only Python stdlib

## Supported Diagram Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Flowchart** 流程图 | Process flows with decisions, start/end nodes | Business logic, login flows, approval chains |
| **Architecture** 架构图 | Service components with connections | System design, microservices, infrastructure |
| **Mind Map** 思维导图 | Hierarchical branches | Brainstorming, knowledge organization |
| **Sequence Diagram** 时序图 | Lifelines with message arrows | API calls, protocol interactions |

## Node Types

| Type | Appearance | Usage |
|------|-----------|-------|
| `terminal` | Green ellipse | Start node |
| `terminal-end` | Red ellipse | End node |
| `process` | Blue-bordered rounded rect | Processing step |
| `decision` | Yellow-bordered diamond | Branch/condition |
| `service` | Purple-bordered rounded rect | Microservice/API |
| `database` | Cyan-bordered rect with thick top bar | Database/storage |
| `success` | Green-bordered rect | Success state |
| `error` | Red-bordered rect | Error/failure state |

## Installation

```bash
# Install via npx (recommended)
npx skills add https://github.com/Program120/interactive-diagram --skill interactive-diagram

# Or manually clone to your skills directory
git clone https://github.com/Program120/interactive-diagram ~/.claude/skills/interactive-diagram
```

## Usage

Just ask Claude Code to draw a diagram in natural language:

```
> 画一个用户登录的流程图

> Draw an architecture diagram for a microservice system

> 帮我画一个项目管理的思维导图

> Create a sequence diagram for OAuth2 authorization flow
```

Claude will start an SSE server, open the browser, and stream nodes/edges in real-time.

## Architecture

```
Agent sends curl commands (~30-50 tokens each)
  → Python SSE Server (scripts/server.py, zero dependencies)
    → Server stores state + broadcasts via SSE
      → template.html renders with AntV X6 + Dagre auto-layout
    → GET /state returns full history (supports page refresh recovery)
```

### Project Structure

```
interactive-diagram/
├── SKILL.md              # Claude Code skill definition
├── README.md             # Documentation
├── LICENSE               # MIT license
├── assets/
│   └── template.html     # Browser renderer (AntV X6 + Dagre)
└── scripts/
    └── server.py         # Python SSE server (zero dependencies)
```

### Server Endpoints

All endpoints support `?s=SESSION_ID` query parameter (default: `default`).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the HTML template |
| `/?s=NAME` | GET | Serve template for a specific session |
| `/events` | GET | SSE event stream |
| `/state` | GET | Return full command history (JSON array) |
| `/status` | GET | Health check with session/client counts |
| `/sessions` | GET | List all sessions with command counts |
| `/cmd` | POST | Send a diagram command |
| `/export` | POST | Export diagram to file (server-side save) |
| `/clear` | POST | Clear session state |

## Server-Side Export

Export diagrams directly to files on disk via curl — no browser interaction needed (browser tab must be open):

```bash
# Export as PNG
curl -s 127.0.0.1:6100/export -d '{"format":"png","path":"/tmp/diagram.png"}'

# Export as SVG
curl -s 127.0.0.1:6100/export -d '{"format":"svg","path":"/tmp/diagram.svg"}'

# Export as Draw.io
curl -s 127.0.0.1:6100/export -d '{"format":"drawio","path":"/tmp/diagram.drawio"}'

# Export as JSON
curl -s 127.0.0.1:6100/export -d '{"format":"json","path":"/tmp/diagram.json"}'

# Omit path to use default (/tmp/diagram-exports/diagram.{ext})
curl -s 127.0.0.1:6100/export -d '{"format":"png"}'

# Export from a specific session
curl -s '127.0.0.1:6100/export?s=arch' -d '{"format":"drawio","path":"~/arch.drawio"}'
```

Supported formats: `png`, `svg`, `json`, `drawio`

## Example

```bash
# Start server + open browser
curl -s http://127.0.0.1:6100/status 2>/dev/null || python3 scripts/server.py &
sleep 1 && open http://127.0.0.1:6100

# Initialize
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"init","title":"用户登录流程","direction":"TB"}'

# Add nodes
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"start","label":"开始","type":"terminal"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"input","label":"输入用户名密码","type":"process"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"check","label":"是否正确?","type":"decision"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"ok","label":"登录成功","type":"success"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"node","id":"fail","label":"显示错误","type":"error"}'

# Add edges
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"start","to":"input"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"input","to":"check"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"check","to":"ok","label":"是","color":"green"}'
curl -s 127.0.0.1:6100/cmd -d '{"cmd":"edge","from":"check","to":"fail","label":"否","color":"red"}'

# Export to file
curl -s 127.0.0.1:6100/export -d '{"format":"png","path":"/tmp/login-flow.png"}'
```

## Contributing

Contributions are welcome! Feel free to:

- Report bugs or suggest features via [Issues](https://github.com/Program120/interactive-diagram/issues)
- Submit Pull Requests for improvements
- Share your diagram examples

## License

[MIT](./LICENSE)
