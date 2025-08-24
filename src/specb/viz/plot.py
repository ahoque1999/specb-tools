# specb/viz/plot.py
import networkx as nx
import specb
from .registry import REGISTRY, _resolve
import inspect

# given a cluster_id and some method, plot the graph with the correct labelling
def network_graph(c, threshold, method, **kwargs):
    G = nx.Graph()

    nodes = specb.io.specbsql.load_c2ls(c, path_d="cutoff_annotation.db", name_t="clusters")

    method_spec = REGISTRY.get(method)
    if method_spec is None:
        raise ValueError(f"Unknown method '{method}'. Available: {list(REGISTRY)}")

    provided = set(kwargs) | {"c"}
    missing = method_spec.required_params - provided
    if missing:
        raise TypeError(f"Method '{method}' requires params: {sorted(missing)}")

    labeller = _resolve(method_spec.labeller_path)
    encoder = _resolve(method_spec.encoder_path)

    sig = inspect.signature(labeller)
    accepted = set(sig.parameters)
    call_args = {k: v for k, v in kwargs.items() if k in accepted}
    if "c" in accepted:
        call_args["c"] = c

    dict_s2label = labeller(nodes, **call_args)
    dict_s2color = encoder(dict_s2label)
    
    for node in nodes:
        G.add_node(node)
    for node in nodes:
        for neighbor, dist in specb.io.archivesql.load_s2n(node, threshold).items():
            G.add_edge(node, neighbor)

    default_color = "yellow"
    node_colors = [dict_s2color.get(n, default_color) for n in G.nodes()]
    pos = nx.kamada_kawai_layout(G)

    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=10, width=0.1)