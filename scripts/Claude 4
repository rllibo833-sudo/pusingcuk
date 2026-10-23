# Mnemos - Quick Reference Card

**Memory is not just storage, it's a living network.**

---

## ⚡ 5-Minute Quick Start

```bash
# 1. Install (one time)
pip install -r requirements.txt

# 2. Start Dashboard
python3 mnemos.py

# 3. Load demo data (optional)
python3 mnemos.py init-demo

# 4. Try commands inside dashboard or use CLI
```

---

## 🎮 Command Cheat Sheet

### Dashboard
```bash
python3 mnemos.py                    # Start interactive dashboard
python3 mnemos.py dashboard          # Same as above
```

### Memory Operations
```bash
python3 mnemos.py add "Title"                              # Add simple note
python3 mnemos.py add "Title" --content "Content here"     # Add with content
python3 mnemos.py add "Title" --type project --tags a,b    # Add with metadata
python3 mnemos.py list                                      # List all memories
python3 mnemos.py search "keyword"                          # Search memories
```

### Knowledge Graph
```bash
python3 mnemos.py graph                          # Show knowledge graph
python3 mnemos.py node add "Concept"            # Add concept node
python3 mnemos.py node add "Name" --description "desc" --type concept
python3 mnemos.py link <source> <target>       # Link two nodes
python3 mnemos.py link <source> <target> --type "uses" --weight 1.5
```

### Analytics
```bash
python3 mnemos.py stats                         # Show statistics
python3 mnemos.py density                       # Show network density
```

### AI Agents
```bash
python3 mnemos.py agents                        # Show agents
python3 mnemos.py agents list                   # List agents
python3 mnemos.py agents add "Claude" --type assistant
```

### Data Management
```bash
python3 mnemos.py export --format json          # Export as JSON
python3 mnemos.py export --format markdown      # Export as Markdown
python3 mnemos.py export -f json -o backup.json # Custom filename
python3 mnemos.py sync                          # Sync with cloud (future)
```

### System
```bash
python3 mnemos.py settings                      # Show settings
python3 mnemos.py help                          # Show help
python3 mnemos.py init-demo                     # Load demo data
```

---

## 📋 Memory Types

| Type | Use Case |
|------|----------|
| **note** | Quick thoughts and ideas |
| **document** | Detailed information |
| **project** | Project tracking |
| **person** | Contact information |
| **concept** | Abstract knowledge |
| **tool** | Resources and tools |

---

## 🏗️ Graph Relationship Types

Common relationship types:
- `related` - General relationship
- `references` - A references B
- `depends_on` - A depends on B
- `uses` - A uses B
- `parent_of` - A is parent of B
- `child_of` - A is child of B
- `similar_to` - Similar concept
- `opposite_of` - Opposite concept

---

## 💡 Common Workflows

### Workflow 1: Learning Topic
```bash
# Create project
python3 mnemos.py add "Learn Python" --type project --tags learning,python

# Add related concepts
python3 mnemos.py node add "Variables"
python3 mnemos.py node add "Functions"
python3 mnemos.py node add "Data Structures"

# Link concepts
python3 mnemos.py link <var_id> <func_id> --type "used_in"
```

### Workflow 2: Project Tracking
```bash
# Create project memory
python3 mnemos.py add "Website Redesign" --type project --tags work,web

# Export progress
python3 mnemos.py export --format json --output project_backup.json

# Track in graph
python3 mnemos.py node add "Frontend"
python3 mnemos.py node add "Backend"
```

### Workflow 3: Research & Notes
```bash
# Add findings
python3 mnemos.py add "Research Finding 1" --content "Details..." --type document
python3 mnemos.py add "Research Finding 2" --content "Details..." --type document

# Search findings
python3 mnemos.py search "specific topic"

# View statistics
python3 mnemos.py stats
```

---

## 🔍 Search Syntax

```bash
# Basic search (searches title, content, tags)
python3 mnemos.py search "python"

# Match multiple words
python3 mnemos.py search "machine learning"

# Tag search
python3 mnemos.py search "python" --tag programming

# Search nodes
python3 mnemos.py node search "neural"
```

---

## 📊 Dashboard Sections

```
┌────────────────────────────────────────────────────┐
│ ▶ Mnemos - Living Knowledge Network               │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────┐  ┌──────────────────────────┐   │
│  │System        │  │Memory Statistics         │   │
│  │Overview      │  │• Total: 3,482            │   │
│  │• Device ID   │  │• Nodes: 2,917            │   │
│  │• Memory: 42% │  │• Edges: 5,842            │   │
│  │• Storage: 12GB │ │• Agents: 6              │   │
│  └──────────────┘  └──────────────────────────┘   │
│                                                    │
│  ┌──────────────┐  ┌──────────────────────────┐   │
│  │Knowledge     │  │Recent Activity           │   │
│  │Graph         │  │• Added "Python" note    │   │
│  │ ● ─ ● ─ ●    │  │• Linked concepts        │   │
│  │  \ │ / │     │  │• Updated Learning Path  │   │
│  │   ●   ●      │  │• Synced with cloud      │   │
│  └──────────────┘  └──────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## ⌨️ Keyboard Shortcuts (Dashboard)

| Key | Action |
|-----|--------|
| `↑↓←→` | Navigate |
| `Enter` | Select |
| `?` | Help |
| `Ctrl+C` | Exit |
| `Ctrl+L` | Clear screen |
| `Tab` | Next section |

---

## 🗂️ Database & Files

```
mnemos/
├── mnemos.db           # SQLite database (auto-created)
├── mnemos_export.json  # JSON export
├── mnemos_memories.md  # Markdown export
├── mnemos.log         # Log file (if running as service)
└── venv/              # Virtual environment (if created)
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Set database location
export MNEMOS_DB_PATH="/custom/path/mnemos.db"

# Set log level
export MNEMOS_LOG_LEVEL="DEBUG"

# Set UI theme
export MNEMOS_THEME="dark"
```

### Python Configuration
In code:
```python
from mnemos_core import MnemosCore

core = MnemosCore()

# Custom database
db = MnemosDatabase("custom_location.db")

# Custom UI
ui = MnemosUI()
ui.display_dashboard()
```

---

## 📱 Terminal Environment Setup

### Termux
```bash
# Enhanced terminal
pkg install less

# Better colors
export TERM=xterm-256color

# Locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### LynOS/Linux
```bash
# Ensure proper locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Optional: Use tmux for better experience
tmux new-session -d -s mnemos 'python3 mnemos.py'
tmux attach -t mnemos
```

### macOS
```bash
# Enable colors
export CLICOLOR=1
export CLICOLOR_FORCE=1

# Use iTerm2 (optional)
# Download dari https://iterm2.com
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | `pip install -r requirements.txt` |
| "Permission denied" | `chmod +x mnemos.py` |
| "Database locked" | `rm mnemos.db-journal` |
| "Display issues" | `export TERM=xterm-256color` |
| "Slow dashboard" | Close other processes, increase RAM |

---

## 📈 Performance Tips

```bash
# Check memory usage
python3 -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Optimize database
sqlite3 mnemos.db "VACUUM; ANALYZE;"

# Clear old activities (keep last 1000)
python3 << 'EOF'
from mnemos_db import MnemosDatabase
db = MnemosDatabase()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('DELETE FROM activities WHERE id NOT IN (SELECT id FROM activities ORDER BY timestamp DESC LIMIT 1000)')
conn.commit()
conn.close()
print("Cleaned up old activities")
EOF
```

---

## 📚 Learning Path Recommendation

1. **Day 1**: Basic commands
   ```bash
   python3 mnemos.py init-demo
   python3 mnemos.py list
   python3 mnemos.py search "python"
   ```

2. **Day 2**: Memory creation
   ```bash
   python3 mnemos.py add "My Topic"
   python3 mnemos.py graph
   ```

3. **Day 3**: Knowledge graph
   ```bash
   python3 mnemos.py node add "Concept"
   python3 mnemos.py link <source> <target>
   ```

4. **Day 4**: Advanced features
   ```bash
   python3 mnemos.py stats
   python3 mnemos.py export --format json
   ```

5. **Day 5**: Read full documentation
   See `README.md` for comprehensive guide

---

## 🎯 Use Cases

### Student
```bash
# Track study materials
python3 mnemos.py add "ML Chapter 3" --type document --tags learning,ml
python3 mnemos.py add "ML Study Plan" --type project

# Build knowledge network
python3 mnemos.py node add "Neural Networks"
python3 mnemos.py graph
```

### Developer
```bash
# Document code learnings
python3 mnemos.py add "Python Context Managers" --type document --tags python,code

# Track project dependencies
python3 mnemos.py add "Project X" --type project
python3 mnemos.py link <project> <dependency>
```

### Researcher
```bash
# Store findings
python3 mnemos.py add "Research Paper Summary" --type document

# Build knowledge graph
python3 mnemos.py node add "Research Topic"
python3 mnemos.py export --format json  # Backup
```

---

## 🌟 Advanced Tips

### Custom Queries
```python
from mnemos_core import MnemosCore

core = MnemosCore()

# Find connections
connections = core.find_connections("node_id", depth=3)

# Get similar memories
similar = core.find_similar_memories("memory_id")

# Custom statistics
density = core.get_memory_density_report()
```

### Batch Operations
```bash
# Add multiple memories from file
while IFS= read -r line; do
  python3 mnemos.py add "$line"
done < list.txt
```

### Automated Backups
```bash
# Daily backup
0 2 * * * cd ~/mnemos && python3 mnemos.py export --format json --output backup_$(date +\%Y\%m\%d).json
```

---

## 📞 Quick Help

```bash
# Show all commands
python3 mnemos.py help

# Command specific help (future feature)
python3 mnemos.py add --help
python3 mnemos.py search --help
```

---

**Happy Memory Building! 🧠💜**

```
Mnemos - Memory for a Smarter You
Memories • Agents • Devices • Forever
```
