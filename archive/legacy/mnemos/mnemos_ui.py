from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich.align import Align
from rich.style import Style
import psutil
import os
from datetime import datetime
from mnemos_db import MnemosDatabase
import time

class MnemosUI:
    def __init__(self):
        self.console = Console()
        self.db = MnemosDatabase()
        self.device_id = self._generate_device_id()
        self.is_running = True
        self.current_view = "dashboard"
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        import hashlib
        hostname = os.environ.get('HOSTNAME', 'termux')
        user = os.environ.get('USER', 'user')
        return hashlib.md5(f"{hostname}-{user}".encode()).hexdigest()[:8]
    
    def get_system_info(self) -> dict:
        """Ambil informasi sistem"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'device_id': f"termux-{self.device_id}",
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / (1024**2),
                'memory_total_mb': memory.total / (1024**2),
                'storage_used_mb': disk.used / (1024**2),
                'storage_total_mb': disk.total / (1024**2),
                'storage_percent': disk.percent,
                'network_status': 'Connected (IPv4)',
                'sync_status': 'Idle',
                'last_sync': '2m ago'
            }
        except:
            return self._get_mock_system_info()
    
    def _get_mock_system_info(self) -> dict:
        """Mock system info untuk testing"""
        return {
            'device_id': f"termux-{self.device_id}",
            'memory_percent': 42,
            'memory_used_mb': 1708,
            'memory_total_mb': 4068,
            'storage_used_mb': 12468,
            'storage_total_mb': 64000,
            'storage_percent': 19.5,
            'network_status': 'Connected (IPv4)',
            'sync_status': 'Idle',
            'last_sync': '2m ago'
        }
    
    def create_system_overview_panel(self) -> Panel:
        """Create System Overview panel"""
        sys_info = self.get_system_info()
        
        overview_text = Text()
        overview_text.append("Device ID        : ", style="dim")
        overview_text.append(f"{sys_info['device_id']}\n")
        overview_text.append("Memory Usage     : ", style="dim")
        overview_text.append(f"{sys_info['memory_percent']:.1f}% ({sys_info['memory_used_mb']:.0f} / {sys_info['memory_total_mb']:.0f})\n")
        overview_text.append("Storage          : ", style="dim")
        overview_text.append(f"{sys_info['storage_used_mb']:.0f} / {sys_info['storage_total_mb']:.0f} MB\n")
        overview_text.append("Sync Status      : ", style="dim")
        overview_text.append(f"{sys_info['sync_status']}\n")
        overview_text.append("Last Sync        : ", style="dim")
        overview_text.append(f"{sys_info['last_sync']}\n")
        overview_text.append("Network          : ", style="dim")
        overview_text.append(f"{sys_info['network_status']}")
        
        return Panel(
            overview_text,
            title="⚙️  System Overview",
            border_style="cyan",
            padding=(1, 2)
        )
    
    def create_memory_statistics_panel(self) -> Panel:
        """Create Memory Statistics panel"""
        total_memories = self.db.get_memory_count()
        total_nodes = self.db.get_node_count()
        total_relationships = self.db.get_relationship_count()
        total_agents = self.db.get_agent_count()
        last_24h = self.db.get_activities_last_24h()
        
        stats_text = Text()
        stats_text.append("Total Memories   : ", style="dim")
        stats_text.append(f"{total_memories}\n")
        stats_text.append("Nodes            : ", style="dim")
        stats_text.append(f"{total_nodes}\n")
        stats_text.append("Relationships    : ", style="dim")
        stats_text.append(f"{total_relationships}\n")
        stats_text.append("Agents           : ", style="dim")
        stats_text.append(f"{total_agents}\n")
        stats_text.append("Last 24h         : ", style="dim")
        stats_text.append(f"+{last_24h}", style="green")
        
        return Panel(
            stats_text,
            title="📊 Memory Statistics",
            border_style="green",
            padding=(1, 2)
        )
    
    def create_knowledge_graph_ascii(self) -> str:
        """Create ASCII representation of knowledge graph"""
        nodes = self.db.get_all_nodes()
        relationships = self.db.get_all_relationships()
        
        if len(nodes) == 0:
            return "    (no nodes yet)"
        
        # Simplified ASCII visualization
        node_count = min(len(nodes), 5)  # Show first 5 nodes
        rel_count = len(relationships)
        
        graph = f"""
    Nodes: {len(nodes)} | Edges: {rel_count}
    
    ●─────● 
    │\   /│
    │ ● ●
    │/   \│
    ●─────●
        """
        return graph
    
    def create_knowledge_graph_panel(self) -> Panel:
        """Create Knowledge Graph panel"""
        nodes = self.db.get_all_nodes()
        relationships = self.db.get_all_relationships()
        
        graph_text = Text()
        if len(nodes) > 0:
            graph_text.append(f"Nodes: {len(nodes)} | Edges: {len(relationships)}\n\n")
            
            # Show top nodes
            for i, node in enumerate(nodes[:5]):
                marker = "●" if i == 0 else "○"
                graph_text.append(f"{marker} {node['label']}\n", style="cyan")
                
                # Show related edges
                related = [r for r in relationships if r['source_id'] == node['id']]
                for rel in related[:2]:
                    graph_text.append(f"  └─ {rel['relationship_type']}\n", style="dim")
            
            if len(nodes) > 5:
                graph_text.append(f"\n... +{len(nodes)-5} more nodes", style="dim")
        else:
            graph_text.append("(No knowledge graph yet)", style="dim")
        
        return Panel(
            graph_text,
            title="🧠 Knowledge Graph",
            border_style="magenta",
            padding=(1, 2)
        )
    
    def create_recent_activity_panel(self) -> Panel:
        """Create Recent Activity panel"""
        activities = self.db.get_recent_activities(limit=5)
        
        activity_text = Text()
        if activities:
            for act in activities:
                time_str = act['timestamp'][-5:]  # Get HH:MM
                activity_text.append(f"● {time_str} ", style="dim")
                activity_text.append(f"{act['action']}: ", style="cyan")
                activity_text.append(f"{act['target_type']}\n")
        else:
            activity_text.append("(No activities yet)", style="dim")
        
        return Panel(
            activity_text,
            title="📋 Recent Activity",
            border_style="yellow",
            padding=(1, 2)
        )
    
    def create_quick_search_panel(self) -> Panel:
        """Create Quick Search panel"""
        search_text = Text()
        search_text.append("🔍 ", style="cyan")
        search_text.append("Search memories, nodes, or relationships...", style="dim")
        search_text.append("\n\nMemories       Python knowledge graph\n", style="dim")
        search_text.append("Projects       Learning Path\n", style="dim")
        search_text.append("People         AI agent collaboration\n", style="dim")
        
        return Panel(
            search_text,
            title="⚡ Quick Search",
            border_style="blue",
            padding=(1, 2)
        )
    
    def create_memory_panel(self) -> Panel:
        """Create Memory notification panel"""
        memory_text = Text()
        memory_text.append("✅ ", style="green")
        memory_text.append("You have 12 new memories\n", style="green")
        
        return Panel(
            memory_text,
            title="🧠 Memory",
            border_style="green",
            padding=(1, 2)
        )
    
    def display_header(self):
        """Display application header"""
        header = Text()
        header.append(" ▶ Mnemos ", style="bold cyan")
        header.append("Living Knowledge Network", style="dim")
        
        self.console.print(header)
        self.console.print("Memory is not just storage, it's a living network.", style="dim")
        self.console.print()
    
    def display_sidebar_menu(self):
        """Display sidebar menu"""
        menu = Table(show_header=False, show_footer=False, padding=(0, 2))
        menu.add_column("Menu", style="cyan")
        
        items = [
            ("▶ Dashboard", "dashboard"),
            ("🧠 Memory Graph", "memory_graph"),
            ("🔍 Search", "search"),
            ("🔄 Sync", "sync"),
            ("🤖 Agents", "agents"),
            ("⚙️  Settings", "settings"),
            ("❓ Help", "help")
        ]
        
        for item, view in items:
            style = "bold green" if view == self.current_view else "dim"
            menu.add_row(item, style=style)
        
        panel = Panel(menu, border_style="blue", padding=(1, 0))
        return panel
    
    def display_dashboard(self):
        """Display main dashboard"""
        self.console.clear()
        self.display_header()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="top", size=3),
            Layout(name="middle"),
            Layout(name="bottom", size=3)
        )
        
        layout["middle"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="system"),
            Layout(name="stats"),
            Layout(name="graph")
        )
        
        layout["right"].split_column(
            Layout(name="activity"),
            Layout(name="search"),
            Layout(name="memory")
        )
        
        # Assign panels
        layout["top"].update(Panel(
            "Mnemos v1.0.0-beta | Terminal v1 | Type 'mnemos help' for commands",
            style="dim"
        ))
        
        layout["system"].update(self.create_system_overview_panel())
        layout["stats"].update(self.create_memory_statistics_panel())
        layout["graph"].update(self.create_knowledge_graph_panel())
        layout["activity"].update(self.create_recent_activity_panel())
        layout["search"].update(self.create_quick_search_panel())
        layout["memory"].update(self.create_memory_panel())
        
        layout["bottom"].update(Panel(
            "Nodes: 2,917 | Edges: 5,842 | (Use arrows to navigate)",
            style="dim"
        ))
        
        self.console.print(layout)
    
    def display_memory_search(self):
        """Display memory search interface"""
        self.console.clear()
        self.display_header()
        self.console.print("[bold cyan]🔍 Memory Search[/bold cyan]\n")
        
        memories = self.db.get_all_memories()
        
        table = Table(title="All Memories", border_style="cyan")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Updated", style="dim")
        table.add_column("Tags", style="green")
        
        for mem in memories[:10]:
            updated = mem['updated_at'][-5:] if mem['updated_at'] else "N/A"
            table.add_row(
                mem['title'],
                mem['type'],
                updated,
                mem['tags'] or "-"
            )
        
        self.console.print(table)
    
    def display_knowledge_graph(self):
        """Display detailed knowledge graph"""
        self.console.clear()
        self.display_header()
        self.console.print("[bold cyan]🧠 Knowledge Graph[/bold cyan]\n")
        
        nodes = self.db.get_all_nodes()
        relationships = self.db.get_all_relationships()
        
        # Nodes table
        node_table = Table(title=f"Nodes ({len(nodes)})", border_style="cyan")
        node_table.add_column("ID", style="cyan")
        node_table.add_column("Label", style="white")
        node_table.add_column("Type", style="magenta")
        
        for node in nodes[:15]:
            node_table.add_row(node['id'][:8], node['label'], node['node_type'])
        
        self.console.print(node_table)
        
        # Relationships table
        self.console.print()
        rel_table = Table(title=f"Relationships ({len(relationships)})", border_style="magenta")
        rel_table.add_column("Source", style="cyan")
        rel_table.add_column("Type", style="yellow")
        rel_table.add_column("Target", style="cyan")
        rel_table.add_column("Weight", style="magenta")
        
        for rel in relationships[:15]:
            rel_table.add_row(
                rel['source_id'][:8],
                rel['relationship_type'],
                rel['target_id'][:8],
                f"{rel['weight']:.1f}"
            )
        
        self.console.print(rel_table)
    
    def display_agents(self):
        """Display AI Agents"""
        self.console.clear()
        self.display_header()
        self.console.print("[bold cyan]🤖 AI Agents[/bold cyan]\n")
        
        agents = self.db.get_all_agents()
        
        if agents:
            table = Table(border_style="cyan")
            table.add_column("Agent ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Status", style="magenta")
            
            for agent in agents:
                status_style = "green" if agent['status'] == 'active' else "dim"
                table.add_row(
                    agent['id'][:8],
                    agent['name'],
                    agent['status'],
                    style=status_style
                )
            
            self.console.print(table)
        else:
            self.console.print("[dim]No agents registered yet[/dim]")
    
    def display_help(self):
        """Display help menu"""
        self.console.clear()
        self.console.print("[bold cyan]📚 Mnemos Help[/bold cyan]\n")
        
        help_text = """
[bold cyan]Commands:[/bold cyan]

[cyan]mnemos dashboard[/cyan]          - Show main dashboard
[cyan]mnemos add[/cyan] <title>         - Add new memory
[cyan]mnemos search[/cyan] <query>      - Search memories
[cyan]mnemos graph[/cyan]               - Show knowledge graph
[cyan]mnemos agents[/cyan]              - List AI agents
[cyan]mnemos sync[/cyan]                - Sync with cloud
[cyan]mnemos settings[/cyan]            - Show settings
[cyan]mnemos help[/cyan]                - Show this help

[bold cyan]Keyboard Shortcuts:[/bold cyan]

[cyan]Ctrl+C[/cyan]    - Exit
[cyan]Arrow Keys[/cyan] - Navigate
[cyan]Enter[/cyan]      - Select
[cyan]?[/cyan]          - Help
        """
        
        self.console.print(help_text)
    
    def run_interactive(self):
        """Run interactive terminal session"""
        self.display_dashboard()
        
        while self.is_running:
            try:
                command = self.console.input("\n[cyan]mnemos>[/cyan] ").strip().lower()
                
                if not command:
                    continue
                
                if command == "dashboard":
                    self.current_view = "dashboard"
                    self.display_dashboard()
                
                elif command.startswith("add "):
                    title = command[4:].strip()
                    self.db.add_memory(
                        f"mem_{int(time.time())}",
                        title,
                        "New memory content",
                        "note",
                        ""
                    )
                    self.console.print("[green]✓ Memory added[/green]")
                    self.display_dashboard()
                
                elif command.startswith("search "):
                    query = command[7:].strip()
                    results = self.db.search_memories(query)
                    self.console.print(f"\n[cyan]Found {len(results)} results for: {query}[/cyan]\n")
                    for mem in results:
                        self.console.print(f"  • {mem['title']}")
                
                elif command == "graph":
                    self.current_view = "graph"
                    self.display_knowledge_graph()
                
                elif command == "agents":
                    self.display_agents()
                
                elif command == "help":
                    self.display_help()
                
                elif command == "clear":
                    self.console.clear()
                
                elif command == "exit" or command == "quit":
                    self.is_running = False
                    self.console.print("[dim]Exiting Mnemos...[/dim]")
                
                else:
                    self.console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
            
            except KeyboardInterrupt:
                self.is_running = False
                self.console.print("\n[dim]Exiting Mnemos...[/dim]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    ui = MnemosUI()
    ui.run_interactive()
