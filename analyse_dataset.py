import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

# 🔥 charger dataset
df = pd.read_csv("dataset_people.csv")

G = nx.Graph()

# 🔹 ajout des nœuds depuis le dataset
for _, row in df.iterrows():
    G.add_node(
        row["name"],
        role=row["status"],
        age=row["age"],
        id=row["id"]
    )

# 🔥 relations aléatoires entre personnes du dataset
import random
all_nodes = list(G.nodes())

edges = [
    (random.choice(all_nodes), random.choice(all_nodes))
    for _ in range(len(all_nodes) * 2)
]

G.add_edges_from(edges)

# icônes
emoji_map = {
    "dealer": "♠",
    "consumer": "●",
    "addict": "⚠",
    "normal": "☺"
}

# couleurs
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

# 🔥 layout plus espacé
pos = nx.spring_layout(G, seed=42, k=2.5, iterations=150)

# labels (icônes uniquement)
labels = {node: emoji_map[G.nodes[node]["role"]] for node in G}

# figure
fig, ax = plt.subplots(figsize=(12, 7))
plt.subplots_adjust(right=0.78)

selected_node = {"node": None}

# légende
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

# 🔥 fonction de dessin
def draw():
    ax.clear()

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.5, edge_color="gray")

    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_color=color_map,
        node_size=800,
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

    ax.set_title("Réseau basé sur dataset_people.csv", fontsize=15)
    ax.axis("off")

    fig.canvas.draw()

draw()

# 🔥 clic précis
def get_node(event):
    for node, (x, y) in pos.items():
        if (x - event.xdata)**2 + (y - event.ydata)**2 < 0.01:
            return node
    return None

def on_press(event):
    if event.inaxes != ax:
        return
    selected_node["node"] = get_node(event)

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

plt.show()