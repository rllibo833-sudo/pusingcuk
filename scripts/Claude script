# Mnemos - Living Knowledge Network

**Memory is not just storage, it's a living network.**

Mnemos adalah platform memori portabel yang dirancang untuk manajemen pengetahuan cerdas dengan knowledge graph lokal, integrasi AI agent, dan terminal interface yang indah.

```
     ▶ Mnemos
       Living Knowledge Network
       Memory is not just storage, it's a living network.
```

## 🎯 Fitur Utama

### 📚 Memory Management
- **Multi-type Memories**: Notes, documents, projects, people, concepts
- **Smart Tagging**: Otomatis categorize dan link memories
- **Search & Discovery**: Full-text search dengan fuzzy matching
- **Version Control**: Track perubahan memories over time

### 🧠 Knowledge Graph
- **Node-based Architecture**: Create concepts, entities, and relationships
- **Relationship Mapping**: Define connections antar memories
- **Graph Visualization**: Interactive graph exploration
- **Density Analysis**: Understand memory network clustering

### 🤖 AI Agent Integration
- **Multi-Agent Support**: ChatGPT, Claude, VS Code, dan custom agents
- **Standard Interface**: MCP (Model Context Protocol) + Skills + API
- **Agent Capabilities**: Extensible skill system untuk agents
- **Context Sharing**: Share memory context antar agents

### 💾 Local-First Storage
- **SQLite Database**: Standalone, portable local database
- **Export Options**: JSON, Markdown, portable formats
- **Cloud Sync**: Optional cloud synchronization (future)
- **Cross-Platform**: Works on macOS, Windows, Linux, Termux

## 📦 Installation

### Requirements
- Python 3.8+
- pip

### Setup

```bash
# Clone atau download files
cd mnemos

# Install dependencies
pip install -r requirements.txt

# Buat executable
chmod +x mnemos.py

# Jalankan
python mnemos.py
```

### Quick Start (Termux)
```bash
$ pip install rich psutil
$ python mnemos.py dashboard
```

## 🚀 Penggunaan

### Interactive Dashboard
```bash
$ python mnemos.py dashboard
# atau shorthand
$ python mnemos.py
```

Dashboard menampilkan:
- **System Overview**: Device info, memory usage, storage
- **Memory Statistics**: Total memories, nodes, relationships, agents
- **Knowledge Graph**: Visual representation of your memory network
- **Recent Activity**: Latest changes dan updates
- **Quick Search**: Fast search across memories

### Menambah Memory

```bash
# Simple note
$ python mnemos.py add "My First Note"

# Dengan content dan tags
$ python mnemos.py add "Python Learning Path" \
  --content "Study plan for machine learning" \
  --type project \
  --tags learning,python,ai

# Supported types:
# - note: Simple notes
# - document: Longer form documents
# - project: Project information
# - person: Contact/person information
# - concept: Abstract concepts
# - tool: Tools dan resources
```

### Searching

```bash
# Search memories
$ python mnemos.py search "python"

# Search akan cari di title, content, dan tags
```

### Knowledge Graph Management

```bash
# Show knowledge graph
$ python mnemos.py graph

# Add concept node
$ python mnemos.py node add "Machine Learning" \
  --description "Study of algorithms learning from data" \
  --type concept

# Link two nodes
$ python mnemos.py link <source_id> <target_id> \
  --type "uses" \
  --weight 1.5
```

### Statistics

```bash
# Show overall statistics
$ python mnemos.py stats

# Show memory density report
$ python mnemos.py density
```

### AI Agent Management

```bash
# List registered agents
$ python mnemos.py agents list

# Add new agent
$ python mnemos.py agents add "Claude" --type assistant
```

### Export Data

```bash
# Export as JSON
$ python mnemos.py export --format json --output my_memories.json

# Export as Markdown
$ python mnemos.py export --format markdown --output memories.md
```

### Demo Initialization

```bash
# Load sample data untuk testing
$ python mnemos.py init-demo
```

## 📁 Project Structure

```
mnemos/
├── mnemos.py           # Main CLI entry point
├── mnemos_core.py      # Core system logic
├── mnemos_db.py        # Database operations
├── mnemos_ui.py        # Terminal UI & Dashboard
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── mnemos.db          # SQLite database (auto-created)
```

## 💡 Core Concepts

### Memory Types
- **Note**: Quick thoughts dan ideas
- **Document**: Detailed information
- **Project**: Project tracking dan goals
- **Person**: Contact dan relationship info
- **Concept**: Abstract knowledge dan principles
- **Tool**: Resources dan tools

### Graph Structure
- **Nodes**: Individual entities (memories, concepts)
- **Relationships**: Connections antara nodes
- **Properties**: Additional metadata per node
- **Weight**: Strength dari relationship

### Activity Tracking
Setiap perubahan dicatat:
- Added memory
- Linked nodes
- Updated content
- Synced with cloud
- Agent interactions

## 🔌 API & Integration

### Import dalam Python

```python
from mnemos_core import MnemosCore
from mnemos_db import MnemosDatabase

# Initialize
core = MnemosCore()

# Create memory
memory_id = core.create_memory(
    title="My Memory",
    content="Content here",
    memory_type="note",
    tags=["important"]
)

# Search
results = core.search_memories("python")

# Get graph
graph = core.get_graph_structure()

# Statistics
stats = core.get_statistics()
```

### AI Agent Integration

```python
from mnemos_core import MnemosCore

core = MnemosCore()

# Register agent
agent_id = core.register_agent(
    name="Claude",
    agent_type="assistant",
    config={"model": "claude-3"}
)

# Agent dapat mengakses memories
memories = core.db.get_all_memories()

# Agent dapat menambah relationships
rel_id = core.add_relationship(
    source_node_id="node_123",
    target_node_id="node_456",
    rel_type="references"
)
```

## 📊 Dashboard Features

### System Overview
```
Device ID        : termux-8f3a2b
Memory Usage     : 42% (1,708 / 4,068 MB)
Storage          : 12,468 / 64,000 MB
Sync Status      : Idle
Last Sync        : 2m ago
Network          : Connected (IPv4)
```

### Memory Statistics
```
Total Memories   : 3,482
Nodes            : 2,917
Relationships    : 5,842
Agents           : 6
Last 24h         : +128
```

### Knowledge Graph
Visualisasi interaktif dari network memories dengan nodes dan edges.

### Recent Activity
Log dari semua perubahan dalam 24 jam terakhir dengan timestamps.

## 🎨 UI/UX

### Terminal Interface
- **Rich Colors**: Syntax highlighting dan colored output
- **Tables & Panels**: Organized information display
- **Interactive Input**: Easy command entry
- **Real-time Updates**: Live dashboard updates

### Shortcuts
- `Ctrl+C`: Exit
- `?`: Help
- Arrow Keys: Navigate
- Enter: Select

## 🔐 Privacy & Security

- **Local Storage**: Semua data disimpan lokal (SQLite)
- **Optional Sync**: Cloud sync fully optional
- **No Tracking**: Tidak ada telemetri
- **Portable**: Single file database untuk backup

## 🚦 Roadmap

### V1.0 (Current)
- ✅ Memory management
- ✅ Knowledge graph
- ✅ SQLite database
- ✅ Terminal UI
- ✅ Agent framework

### V1.1 (Planned)
- [ ] Cloud sync
- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Advanced graph visualization

### V2.0 (Future)
- [ ] Vector embeddings
- [ ] AI-powered insights
- [ ] Semantic search
- [ ] Multi-user support

## 📝 Examples

### Example 1: Study System

```bash
# Create project
$ python mnemos.py add "Machine Learning Study" \
  --type project \
  --tags learning,ml

# Add related concepts
$ python mnemos.py node add "Neural Networks"
$ python mnemos.py node add "Deep Learning"
$ python mnemos.py node add "Training"

# Link them
$ python mnemos.py link <nn_id> <dl_id> --type "parent_of"
$ python mnemos.py link <training_id> <nn_id> --type "used_in"
```

### Example 2: Knowledge Capture

```bash
# Record insights
$ python mnemos.py add "GraphDB Insights" \
  --content "Graph databases are better for relationships" \
  --type document \
  --tags database,graph

# Link to related memory
$ python mnemos.py link <memory1_id> <memory2_id> --type "references"
```

### Example 3: Project Tracking

```bash
# Create project memory
$ python mnemos.py add "Website Redesign" \
  --type project \
  --tags work,project,web

# Export progress
$ python mnemos.py export --format json --output project_backup.json
```

## 🤝 Contributing

Contributions welcome! Areas untuk improvement:
- UI enhancements
- Performance optimization
- Additional export formats
- Integration dengan more AI providers

## 📄 License

MIT License

## 🙋 FAQ

**Q: Bagaimana cara backup data?**
A: Gunakan `export` command atau copy `mnemos.db` file.

**Q: Apakah bisa digunakan offline?**
A: Ya, sepenuhnya offline. Cloud sync adalah optional.

**Q: Berapa banyak memories yang bisa disimpan?**
A: Tidak ada limit hard, tergantung storage device.

**Q: Apakah bisa sinkron dengan cloud?**
A: Planned untuk v1.1. Saat ini hanya local storage.

**Q: Apakah bisa digunakan dengan Termux?**
A: Ya! Fully compatible dengan Termux.

---

**Made with 💜 for smarter memory management**

```
 ▶ Mnemos
   Living Knowledge Network
   Memories • Agents • Devices • Forever
```
