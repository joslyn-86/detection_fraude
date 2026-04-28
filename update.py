import networkx as nx
import matplotlib.pyplot as plt
import random
from matplotlib.lines import Line2D

# 🔥 distribution contrôlée (IMPORTANT)
n_normal = random.randint(30, 50)
n_consumer = random.randint(10, 15)
n_addict = random.randint(2, 4)
n_dealer = random.randint(3, 5)

G = nx.Graph()
nodes = {}

# 🔹 normal (majorité)
for i in range(n_normal):
    nodes[f"N{i}"] = "normal"

# 🔹 consumer
for i in range(n_consumer):
    nodes[f"C{i}"] = "consumer"

# 🔹 addict
for i in range(n_addict):
    nodes[f"A{i}"] = "addict"

# 🔹 dealer (rare)
for i in range(n_dealer):
    nodes[f"D{i}"] = "dealer"

# ajout au graphe
for node, role in nodes.items():
    G.add_node(node, role=role)

# relations aléatoires
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

# couleurs des nœuds
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

# position
pos = nx.spring_layout(G, seed=42, k=1.2, iterations=100)

# labels
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

# 🎨 couleur des arêtes
def get_edge_colors():
    edge_colors = []

    for u, v in G.edges():
        ru = G.nodes[u]["role"]
        rv = G.nodes[v]["role"]

        # priorité
        if ru == "dealer" or rv == "dealer":
            edge_colors.append("#e74c3c")  # rouge
        elif ru == "addict" or rv == "addict":
            edge_colors.append("#e67e22")  # orange
        elif ru == "consumer" or rv == "consumer":
            edge_colors.append("#3498db")  # bleu
        else:
            edge_colors.append("#2ecc71")  # vert

    return edge_colors


def draw():
    ax.clear()

    # arêtes colorées
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=get_edge_colors(),
        alpha=0.8,
        width=2
    )

    # nœuds
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=color_map,
        node_size=500,
        edgecolors="black"
    )

    # labels
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

# clic
def on_press(event):
    if event.inaxes != ax:
        return

    for node, (x, y) in pos.items():
        if (x - event.xdata)**2 + (y - event.ydata)**2 < 0.02:
            selected_node["node"] = node
            break

# drag
def on_motion(event):
    if selected_node["node"] is None:
        return
    if event.inaxes != ax:
        return

    node = selected_node["node"]
    pos[node] = (event.xdata, event.ydata)
    draw()

# release
def on_release(event):
    selected_node["node"] = None

fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

plt.show()