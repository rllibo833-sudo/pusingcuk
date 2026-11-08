import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import os

class MnemosDatabase:
    def __init__(self, db_path: str = "mnemos.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inisialisasi database dengan skema lengkap"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel Memories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT DEFAULT 'note',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                color TEXT DEFAULT '#2E7D32'
            )
        ''')
        
        # Tabel Nodes (untuk graph)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                memory_id TEXT,
                node_type TEXT,
                label TEXT NOT NULL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        ''')
        
        # Tabel Relationships (untuk graph connections)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES nodes(id),
                FOREIGN KEY (target_id) REFERENCES nodes(id)
            )
        ''')
        
        # Tabel Agents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'idle',
                last_activity TIMESTAMP,
                config TEXT
            )
        ''')
        
        # Tabel Activities (untuk Recent Activity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                target_id TEXT,
                target_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT,
                details TEXT
            )
        ''')
        
        # Tabel System Stats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                memory_usage_percent REAL,
                storage_used_mb REAL,
                network_status TEXT,
                sync_status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ===== MEMORY OPERATIONS =====
    def add_memory(self, memory_id: str, title: str, content: str, memory_type: str = "note", tags: str = "") -> bool:
        """Tambah memory baru"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO memories (id, title, content, type, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (memory_id, title, content, memory_type, tags))
            
            # Catat activity
            self._add_activity("Added memory", memory_id, "memory", agent_id="system")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding memory: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_memories(self) -> List[Dict]:
        """Ambil semua memories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM memories ORDER BY updated_at DESC')
        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return memories
    
    def search_memories(self, query: str) -> List[Dict]:
        """Search memories by title atau content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM memories 
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_memory_count(self) -> int:
        """Hitung total memories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM memories')
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    # ===== NODE & RELATIONSHIP OPERATIONS =====
    def add_node(self, node_id: str, memory_id: str, node_type: str, label: str, properties: dict = None) -> bool:
        """Tambah node untuk knowledge graph"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            props_json = json.dumps(properties) if properties else '{}'
            cursor.execute('''
                INSERT INTO nodes (id, memory_id, node_type, label, properties)
                VALUES (?, ?, ?, ?, ?)
            ''', (node_id, memory_id, node_type, label, props_json))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding node: {e}")
            return False
        finally:
            conn.close()
    
    def add_relationship(self, rel_id: str, source_id: str, target_id: str, rel_type: str, weight: float = 1.0) -> bool:
        """Tambah relationship antar nodes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO relationships (id, source_id, target_id, relationship_type, weight)
                VALUES (?, ?, ?, ?, ?)
            ''', (rel_id, source_id, target_id, rel_type, weight))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_nodes(self) -> List[Dict]:
        """Ambil semua nodes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM nodes')
        nodes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return nodes
    
    def get_all_relationships(self) -> List[Dict]:
        """Ambil semua relationships"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM relationships')
        rels = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rels
    
    def get_node_count(self) -> int:
        """Hitung total nodes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM nodes')
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def get_relationship_count(self) -> int:
        """Hitung total relationships"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM relationships')
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    # ===== SYSTEM OPERATIONS =====
    def record_system_stats(self, memory_percent: float, storage_mb: float, network_status: str, sync_status: str):
        """Catat system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_stats (memory_usage_percent, storage_used_mb, network_status, sync_status)
            VALUES (?, ?, ?, ?)
        ''', (memory_percent, storage_mb, network_status, sync_status))
        conn.commit()
        conn.close()
    
    def get_latest_stats(self) -> Dict:
        """Ambil latest system stats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM system_stats 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ===== ACTIVITY OPERATIONS =====
    def _add_activity(self, action: str, target_id: str, target_type: str, agent_id: str = "system", details: str = ""):
        """Catat activity (internal)"""
        import uuid
        conn = self.get_connection()
        cursor = conn.cursor()
        activity_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO activities (id, action, target_id, target_type, agent_id, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (activity_id, action, target_id, target_type, agent_id, details))
        conn.commit()
        conn.close()
    
    def get_recent_activities(self, limit: int = 20) -> List[Dict]:
        """Ambil recent activities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM activities 
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return activities
    
    def get_activities_last_24h(self) -> int:
        """Hitung activities dalam 24 jam terakhir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        since = datetime.now() - timedelta(hours=24)
        cursor.execute('''
            SELECT COUNT(*) as count FROM activities 
            WHERE timestamp > ?
        ''', (since,))
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    # ===== AGENT OPERATIONS =====
    def register_agent(self, agent_id: str, name: str, config: dict = None) -> bool:
        """Register AI agent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            config_json = json.dumps(config) if config else '{}'
            cursor.execute('''
                INSERT OR REPLACE INTO agents (id, name, status, config)
                VALUES (?, ?, 'idle', ?)
            ''', (agent_id, name, config_json))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error registering agent: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_agents(self) -> List[Dict]:
        """Ambil semua agents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, status FROM agents')
        agents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return agents
    
    def get_agent_count(self) -> int:
        """Hitung total agents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM agents')
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE agents SET status = ?, last_activity = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, agent_id))
        conn.commit()
        conn.close()
