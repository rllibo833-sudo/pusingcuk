#!/usr/bin/env python3
"""
Example Usage of Mnemos Core API
Demonstrates programmatic usage of the Mnemos system
"""

from mnemos_core import MnemosCore, MemoryTemplate
from mnemos_db import MnemosDatabase
import json

def example_basic_memories():
    """Example 1: Create and search basic memories"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Memory Operations")
    print("="*60)
    
    core = MnemosCore()
    
    # Create some memories
    mem1 = core.create_memory(
        title="Python Fundamentals",
        content="Variables, loops, functions, and data structures...",
        memory_type="document",
        tags=["python", "programming", "tutorial"]
    )
    print(f"✓ Created memory: {mem1}")
    
    mem2 = core.create_memory(
        title="Graph Databases",
        content="Neo4j, knowledge graphs, relationship mapping...",
        memory_type="document",
        tags=["database", "graphs", "technology"]
    )
    print(f"✓ Created memory: {mem2}")
    
    mem3 = core.create_memory(
        title="AI Agent Development",
        content="Building intelligent agents with LLMs...",
        memory_type="project",
        tags=["ai", "agents", "development"]
    )
    print(f"✓ Created memory: {mem3}")
    
    # Search
    print("\nSearching for 'python'...")
    results = core.search_memories("python")
    for mem in results:
        print(f"  → {mem['title']} ({mem['type']})")
    
    # List all
    print("\nAll memories:")
    all_mems = core.db.get_all_memories()
    for mem in all_mems:
        print(f"  → {mem['title']}")

def example_knowledge_graph():
    """Example 2: Build a knowledge graph"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Knowledge Graph Operations")
    print("="*60)
    
    core = MnemosCore()
    
    # Create concept nodes
    print("Creating concept nodes...")
    node_ml = core.add_concept_node(
        concept_name="Machine Learning",
        description="The field of study for algorithms learning from data"
    )
    print(f"✓ Created ML node: {node_ml}")
    
    node_nn = core.add_concept_node(
        concept_name="Neural Networks",
        description="Computational models inspired by biological neurons"
    )
    print(f"✓ Created NN node: {node_nn}")
    
    node_dl = core.add_concept_node(
        concept_name="Deep Learning",
        description="Multiple layers of neural networks"
    )
    print(f"✓ Created DL node: {node_dl}")
    
    node_training = core.add_concept_node(
        concept_name="Model Training",
        description="Process of teaching models"
    )
    print(f"✓ Created Training node: {node_training}")
    
    # Create relationships
    print("\nCreating relationships...")
    
    rel1 = core.add_relationship(
        source_node_id=node_ml,
        target_node_id=node_nn,
        rel_type="includes",
        weight=1.0
    )
    print(f"✓ ML → NN: includes")
    
    rel2 = core.add_relationship(
        source_node_id=node_nn,
        target_node_id=node_dl,
        rel_type="parent_of",
        weight=1.0
    )
    print(f"✓ NN → DL: parent_of")
    
    rel3 = core.add_relationship(
        source_node_id=node_training,
        target_node_id=node_ml,
        rel_type="used_in",
        weight=0.8
    )
    print(f"✓ Training → ML: used_in")
    
    # Get graph structure
    print("\nGraph Statistics:")
    graph = core.get_graph_structure()
    print(f"  Total Nodes: {graph['stats']['total_nodes']}")
    print(f"  Total Edges: {graph['stats']['total_edges']}")
    print(f"  Node Types: {graph['stats']['node_types']}")

def example_memory_linking():
    """Example 3: Link memories into graph"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Link Memories in Knowledge Graph")
    print("="*60)
    
    core = MnemosCore()
    
    # Create memories
    print("Creating related memories...")
    
    mem_study = core.create_memory(
        title="ML Study Plan",
        content="A comprehensive plan to learn machine learning...",
        memory_type="project",
        tags=["learning", "ml", "plan"]
    )
    print(f"✓ Study Plan: {mem_study}")
    
    mem_course = core.create_memory(
        title="Coursera ML Course",
        content="Andrew Ng's machine learning course review...",
        memory_type="document",
        tags=["learning", "ml", "course", "resource"]
    )
    print(f"✓ Course: {mem_course}")
    
    # Link them
    print("\nLinking memories...")
    linked = core.link_memories(
        source_memory_id=mem_study,
        target_memory_id=mem_course,
        relationship="uses_resource"
    )
    
    if linked:
        print("✓ Memories linked successfully")
    
    # Find similar
    print("\nFinding similar memories...")
    similar = core.find_similar_memories(mem_study)
    for mem_id, score in similar:
        print(f"  → Similarity: {score:.2%}")

def example_agents():
    """Example 4: Register and manage AI agents"""
    print("\n" + "="*60)
    print("EXAMPLE 4: AI Agent Management")
    print("="*60)
    
    core = MnemosCore()
    
    # Register agents
    print("Registering AI agents...")
    
    agent_claude = core.register_agent(
        name="Claude",
        agent_type="assistant",
        config={
            "model": "claude-3-sonnet",
            "capabilities": ["reasoning", "analysis", "coding"]
        }
    )
    print(f"✓ Registered Claude: {agent_claude}")
    
    agent_gpt = core.register_agent(
        name="ChatGPT",
        agent_type="assistant",
        config={
            "model": "gpt-4",
            "capabilities": ["conversation", "coding", "analysis"]
        }
    )
    print(f"✓ Registered ChatGPT: {agent_gpt}")
    
    agent_copilot = core.register_agent(
        name="GitHub Copilot",
        agent_type="code_generator",
        config={
            "model": "copilot",
            "capabilities": ["code_generation", "code_completion"]
        }
    )
    print(f"✓ Registered Copilot: {agent_copilot}")
    
    # List agents
    print("\nRegistered agents:")
    agents = core.get_available_agents()
    for agent in agents:
        print(f"  → {agent['name']}: {agent['status']}")

def example_statistics():
    """Example 5: Get statistics and analytics"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Statistics & Analytics")
    print("="*60)
    
    core = MnemosCore()
    
    # Get stats
    stats = core.get_statistics()
    
    print("\nMemory Statistics:")
    print(f"  Total Memories: {stats['memories']['total']}")
    print(f"  By Type:")
    for mem_type, count in stats['memories']['by_type'].items():
        print(f"    - {mem_type}: {count}")
    
    print("\nGraph Statistics:")
    print(f"  Total Nodes: {stats['graph']['total_nodes']}")
    print(f"  Total Edges: {stats['graph']['total_edges']}")
    print(f"  Node Types: {stats['graph']['node_types']}")
    print(f"  Relationship Types: {stats['graph']['relationship_types']}")
    
    print("\nActivity Statistics:")
    print(f"  Changes (Last 24h): +{stats['activity']['last_24h']}")
    
    # Get density report
    print("\nMemory Density Report:")
    density = core.get_memory_density_report()
    print(f"  Avg Connections per Node: {density['average_connections_per_node']:.2f}")
    print(f"  Total Nodes: {density['total_nodes']}")
    print(f"  Isolated Nodes: {density['isolated_nodes']}")
    print(f"  Network Density: {density['network_density']:.4f}")

def example_export():
    """Example 6: Export data"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Export Data")
    print("="*60)
    
    core = MnemosCore()
    
    # Export as JSON
    print("Exporting as JSON...")
    if core.export_graph_json("mnemos_export.json"):
        print("✓ Exported to mnemos_export.json")
    
    # Export as Markdown
    print("Exporting as Markdown...")
    if core.export_memories_markdown("mnemos_memories.md"):
        print("✓ Exported to mnemos_memories.md")

def example_comprehensive():
    """Example 7: Comprehensive workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Comprehensive Workflow")
    print("="*60)
    
    core = MnemosCore()
    
    # Clear and start fresh
    db = MnemosDatabase()
    
    print("\n1. Creating Project Memory...")
    project = core.create_memory(
        title="AI Agent System Design",
        content="Designing a system for multiple AI agents to collaborate...",
        memory_type="project",
        tags=["ai", "agents", "system-design", "work"]
    )
    
    print("\n2. Adding Concept Nodes...")
    node_agent = core.add_concept_node("Agent", "Autonomous entity")
    node_collaboration = core.add_concept_node("Collaboration", "Working together")
    node_memory = core.add_concept_node("Memory", "Information storage")
    node_graph = core.add_concept_node("Knowledge Graph", "Network of relationships")
    
    print("\n3. Creating Relationships...")
    core.add_relationship(node_agent, node_collaboration, "enables", 1.0)
    core.add_relationship(node_collaboration, node_memory, "requires", 1.0)
    core.add_relationship(node_memory, node_graph, "uses", 1.0)
    
    print("\n4. Registering Agents...")
    agent1 = core.register_agent("Analyst", "analyzer")
    agent2 = core.register_agent("Designer", "designer")
    
    print("\n5. Getting Statistics...")
    stats = core.get_statistics()
    print(f"   Total Memories: {stats['memories']['total']}")
    print(f"   Total Nodes: {stats['graph']['total_nodes']}")
    print(f"   Total Edges: {stats['graph']['total_edges']}")
    
    print("\n6. Exporting Results...")
    core.export_graph_json("workflow_result.json")
    
    print("\n✓ Workflow completed successfully!")

def main():
    """Run all examples"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         Mnemos - Living Knowledge Network Examples         ║")
    print("║                                                            ║")
    print("║  Memory is not just storage, it's a living network.       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        # Initialize demo data first
        core = MnemosCore()
        
        example_basic_memories()
        example_knowledge_graph()
        example_memory_linking()
        example_agents()
        example_statistics()
        example_export()
        example_comprehensive()
        
        print("\n" + "="*60)
        print("All examples completed successfully! ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
