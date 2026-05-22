import networkx as nx
import matplotlib.pyplot as plt
import random
from matplotlib.lines import Line2D
from neo4j import GraphDatabase

# ==============================
#  CONFIG NEO4J
# ==============================
uri = "bolt://127.0.0.1:7687"
user = "neo4j"
password = "132465samuel"  
driver = GraphDatabase.driver(uri, auth=(user, password))

# ==============================
#  GENERATION DU GRAPHE
# ==============================
n_normal = random.randint(30, 50)
n_consumer = random.randint(10, 15)
n_addict = random.randint(2, 4)
n_dealer = random.randint(3, 5)

G = nx.Graph()
nodes = {}

for i in range(n_normal):
    nodes[f"N{i}"] = "normal"

for i in range(n_consumer):
    nodes[f"C{i}"] = "consumer"

for i in range(n_addict):
    nodes[f"A{i}"] = "addict"

for i in range(n_dealer):
    nodes[f"D{i}"] = "dealer"

for node, role in nodes.items():
    G.add_node(node, role=role)

all_nodes = list(G.nodes())

edges = [
    (random.choice(all_nodes), random.choice(all_nodes))
    for _ in range(len(all_nodes) * 2)
]

G.add_edges_from(edges)


emoji_map = {
    "dealer": "♠",
    "consumer": "●",
    "addict": "⚠",
    "normal": "☺"
}

color_map = []
for node in G:
    role = G.nodes[node]["role"]
    if role == "dealer":
        color_map.append("#f39c12")
    elif role == "consumer":
        color_map.append("#3498db")
    elif role == "addict":
        color_map.append("#e74c3c")
    else:
        color_map.append("#2ecc71")

pos = nx.spring_layout(G, seed=42, k=1.2, iterations=100)
labels = {node: emoji_map[G.nodes[node]["role"]] for node in G}

fig, ax = plt.subplots(figsize=(12, 7))
plt.subplots_adjust(right=0.78)

selected_node = {"node": None}

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='♠ Dealer',
           markerfacecolor='#f39c12', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='● Consumer',
           markerfacecolor='#3498db', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='⚠ Addict',
           markerfacecolor='#e74c3c', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='☺ Normal',
           markerfacecolor='#2ecc71', markersize=10)
]

def get_edge_colors():
    edge_colors = []
    for u, v in G.edges():
        ru = G.nodes[u]["role"]
        rv = G.nodes[v]["role"]

        if ru == "dealer" or rv == "dealer":
            edge_colors.append("#e74c3c")
        elif ru == "addict" or rv == "addict":
            edge_colors.append("#e67e22")
        elif ru == "consumer" or rv == "consumer":
            edge_colors.append("#3498db")
        else:
            edge_colors.append("#2ecc71")
    return edge_colors


def draw():
    ax.clear()

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=get_edge_colors(),
        alpha=0.8,
        width=2
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=color_map,
        node_size=500,
        edgecolors="black"
    )

    nx.draw_networkx_labels(
        G, pos,
        ax=ax,
        labels=labels,
        font_size=16
    )

    ax.legend(handles=legend_elements,
              loc='center left',
              bbox_to_anchor=(1, 0.5))

    ax.set_title("Réseau de diffusion (modèle réaliste)", fontsize=15)
    ax.axis("off")

    fig.canvas.draw()

draw()
def get_stats():
    with driver.session() as session:

        nodes = session.execute_read(lambda tx: tx.run(
            "MATCH (n) RETURN count(n) AS total"
        ).single()["total"])

        rels = session.execute_read(lambda tx: tx.run(
            "MATCH ()-[r]->() RETURN count(r) AS total"
        ).single()["total"])

        roles = session.execute_read(lambda tx: tx.run("""
            MATCH (n)
            RETURN n.role AS role, count(*) AS count
        """).data())

    print("\nSTATISTIQUES DU GRAPHE")
    print("------------------------")
    print(f"Nodes : {nodes}")
    print(f"Relations : {rels}")
    print("\nRépartition :")
    for r in roles:
        print(f"   {r['role']} : {r['count']}")

def on_press(event):
    if event.inaxes != ax:
        return

    for node, (x, y) in pos.items():
        if (x - event.xdata)**2 + (y - event.ydata)**2 < 0.02:
            selected_node["node"] = node
            break

def on_motion(event):
    if selected_node["node"] is None:
        return
    if event.inaxes != ax:
        return

    node = selected_node["node"]
    pos[node] = (event.xdata, event.ydata)
    draw()

def on_release(event):
    selected_node["node"] = None

fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

#  ENVOI VERS NEO4J

def create_nodes(tx, nodes):
    query = """
    UNWIND $nodes AS node
    MERGE (n:Person {id: node.id})
    SET n.role = node.role
    """
    tx.run(query, nodes=nodes)


def create_edges(tx, edges):
    query = """
    UNWIND $edges AS edge
    MATCH (a:Person {id: edge.source})
    MATCH (b:Person {id: edge.target})
    MERGE (a)-[:CONNECTED_TO]-(b)
    """
    tx.run(query, edges=edges)

get_stats()
def send_to_neo4j():
    nodes_data = [{"id": n, "role": G.nodes[n]["role"]} for n in G.nodes()]
    edges_data = [{"source": u, "target": v} for u, v in G.edges()]

    with driver.session() as session:
        session.execute_write(create_nodes, nodes_data)
        session.execute_write(create_edges, edges_data)

    print("Données envoyées dans Neo4j !")
#  EXECUTION
if __name__ == "__main__":
    send_to_neo4j()
    plt.show()
    driver.close()