<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill" />
  <img src="https://img.shields.io/badge/Zero-Dependencies-success?style=for-the-badge" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/HTML5-Interactive-orange?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
</p>

<h1 align="center">Interactive Diagram</h1>

<p align="center">
  <strong>Generate interactive, draggable HTML diagrams as standalone files — zero dependencies, works everywhere.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#supported-diagram-types">Diagram Types</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Features

- **Zero Dependencies** — Single HTML file, no CDN, no npm, no build step
- **Drag & Drop** — All nodes are draggable with mouse and touch support
- **Auto Layout** — Dagre-based hierarchical layout algorithm built-in
- **Pan & Zoom** — Canvas panning and toolbar zoom controls
- **Export** — PNG, SVG, and JSON export out of the box
- **Modern UI** — Clean design with shadows, gradients, and smooth animations
- **Responsive** — Works on desktop and mobile browsers
- **Bilingual** — Supports both Chinese and English content

## Supported Diagram Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Flowchart** 流程图 | Process flows with decisions, start/end nodes | Business logic, login flows, approval chains |
| **Architecture** 架构图 | Service components with grouped containers | System design, microservices, infrastructure |
| **Mind Map** 思维导图 | Radial hierarchical branches | Brainstorming, knowledge organization |
| **Sequence Diagram** 时序图 | Lifelines with message arrows | API calls, protocol interactions |

## Installation

```bash
# Install via Claude Code CLI
claude skill install --url https://github.com/Program120/interactive-diagram
```

## Usage

Just ask Claude Code to draw a diagram in natural language:

```
> 画一个用户登录的流程图

> Draw an architecture diagram for a microservice system

> 帮我画一个项目管理的思维导图

> Create a sequence diagram for OAuth2 authorization flow
```

Claude will generate a standalone `.html` file and open it in your browser.

## Examples

### Flowchart

```
User Request → Input Validation → [Valid?]
                                    ├─ Yes → Process Data → Return Result
                                    └─ No  → Show Error → Retry
```

### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Frontend                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  React   │  │  Next.js │  │  Mobile  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼──────────────┼─────────────┼────────┘
        │              │             │
        ▼              ▼             ▼
┌─────────────────────────────────────────────┐
│  API Gateway (Nginx / Kong)                 │
└──────────────────┬──────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│ Auth    │ │ Business │ │ Payment  │
│ Service │ │ Service  │ │ Service  │
└────┬────┘ └────┬─────┘ └────┬─────┘
     │           │             │
     ▼           ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│  Redis  │ │  MySQL   │ │  MQ      │
└─────────┘ └──────────┘ └──────────┘
```

### Mind Map

```
                    ┌─ Frontend ─── React / Vue / Angular
                    │
Project ────────────┼─ Backend ──── Node.js / Python / Go
                    │
                    ├─ Database ─── MySQL / Redis / MongoDB
                    │
                    └─ DevOps ──── Docker / K8s / CI/CD
```

## How It Works

1. You describe what you want in natural language
2. Claude Code analyzes the structure and relationships
3. A standalone HTML file is generated with:
   - Dagre auto-layout for optimal node positioning
   - SVG bezier curves for connections
   - Full drag-and-drop interactivity
   - Export capabilities (PNG / SVG / JSON)
4. The file opens automatically in your default browser

## Tech Stack

This skill generates pure HTML/CSS/JS with these techniques built-in:

- **Layout**: Dagre algorithm (embedded, no external lib)
- **Rendering**: DOM nodes + SVG connections
- **Interaction**: Vanilla JS drag/drop, pan, zoom
- **Export**: Canvas API (PNG), SVG serialization, JSON dump

## Contributing

Contributions are welcome! Feel free to:

- Report bugs or suggest features via [Issues](https://github.com/Program120/interactive-diagram/issues)
- Submit Pull Requests for improvements
- Share your diagram examples

## License

MIT

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/Program120">Program120</a> & <a href="https://claude.ai">Claude</a>
</p>
</content>
</invoke>