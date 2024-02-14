import networkx as nx
import matplotlib.pyplot as plt
import textwrap
import pickle
from typing import List

def define_nodes() -> List:
    """The nodes for the topics in the graph

    Args:
        None

    Returns:
        List [financial_metrics, participants, sentiment, hiring_needs]
    """
    # Financial metrics
    financial_metrics = [
        "Revenue growth (15% year-over-year)",
        "Gross margin improvement (2 percentage points)",
        "Operating income increase (20% year-over-year)",
        "Positive free cash flow ($50 million)"
    ]

    # Companies represented in participants asking questions
    participants = [
        "Wells Fargo",
        "JP Morgan",
        "State Street"
    ]

    # Overall sentiment
    sentiment = "Positive"

    # Specific skills and talents company is actively seeking to hire
    hiring_needs = [
        "Data analytics",
        "AI and ML",
        "Software development",
        "Strong leadership capabilities"
    ]

    return financial_metrics, participants, sentiment, hiring_needs

def create_graph() -> nx.Graph:
    """Build the graph manually using NetworkX by adding the nodes and edges 
    from a defined schema designed to answer only these questions:
    (1) What are the key financial metrics discussed during the earnings call?
    (2) What companies were represented in the participants who asked questions?
    (3) What is the overall sentiment of investors towards BNY Mellon?
    (4) What specific skills and talents is BNY Mellon actively seeking to hire?

    Args:
        None

    Returns:
        NetworkX Graph modeling the desired relationships to answer the 4 question types
    """
    # Create an empty graph
    G = nx.Graph()

    # Add nodes for entities
    company = "BNY Mellon"
    G.add_node(company, label=company)
    G.add_node("Financial Metrics", label="Financial Metrics")
    G.add_node("Participants", label="Participants")
    G.add_node("Sentiment", label="Sentiment")
    G.add_node("Hiring Needs", label="Hiring Needs")

    # Add edges to represent relationships
    G.add_edge(company, "Financial Metrics", relation="discusses")
    G.add_edge(company, "Participants", relation="represented by")
    G.add_edge(company, "Sentiment", relation="impacts")
    G.add_edge(company, "Hiring Needs", relation="seeks")

    # Add specific data as nodes and connect them to respective entities
    financial_metrics, participants, sentiment, hiring_needs = define_nodes()

    for metric in financial_metrics:
        G.add_node(metric, label=metric)
        G.add_edge("Financial Metrics", metric)

    for participant in participants:
        G.add_node(participant, label=participant)
        G.add_edge("Participants", participant)

    G.add_node(sentiment, label=sentiment)
    G.add_edge("Sentiment", sentiment)

    for need in hiring_needs:
        G.add_node(need, label=need)
        G.add_edge("Hiring Needs", need)
    
    return G

def visualize_graph(G: nx.Graph) -> None:
    """Visualize the sample knowledge graph

    Args:
        G: the NetworkX graph created

    Returns:
        None
    """
    pos = nx.spring_layout(G)  # positions for all nodes

    # Ensure all nodes have the 'label' attribute
    for node in G.nodes():
        if 'label' not in G.nodes[node]:
            G.nodes[node]['label'] = node  # Default to the node name if label not provided

    # Calculate node sizes dynamically based on the length of the text
    node_sizes = [len(G.nodes[node]['label']) * 300 for node in G.nodes()]

    # Draw nodes
    nx.draw(G, pos, with_labels=True, labels={node: textwrap.fill(G.nodes[node]['label'], width=15) for node in G.nodes()},
            font_weight='bold', node_size=node_sizes, node_color='skyblue', font_size=10)

    # Display the graph
    plt.show()

def traverse_graph(G: nx.Graph, node: str) -> List:
    """Find the answers within the nodes

    Args:
        G: the sample knowledge graph
        node: the topic based on the user query

    Returns:
        relevant_answers: List of the nodes to answer user query
    """
    # Get the neighbors of the company node
    neighbors = list(G.neighbors("BNY Mellon"))

    # Find the relevant nodes to answer user query
    relevant_answers = []
    for neighbor in neighbors:
        if neighbor == node:
            relevant_answers.extend(list(G.neighbors(neighbor)))
    relevant_answers.remove('BNY Mellon') # bug that adds BNY because it is technically a neighbor
    return relevant_answers

if __name__ == "__main__":
    print("Creating the knowledge graph...")
    G = create_graph()

    file_name = "sample_knowledge_graph.pickle"
    print(f"Saving the knowledge graph as {file_name}...")
    with open(file_name, "wb") as f:
        pickle.dump(G, f) # save graph

    print("Visualizing the knowledge graph...")
    visualize_graph(G)
    