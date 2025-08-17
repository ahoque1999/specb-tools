# specb/viz/plot.py
import importlib
from typing import Any
from dataclasses import dataclass, field
from .registry import REGISTRY
import networkx as nx
import specb

# given a cluster_id and some method, plot the graph with the correct labelling

@dataclass
class MethodSpec:
    labeller_path: str              
    encoder_path: str              
    required_params: set[str] = field(default_factory=set)
    defaults: dict = field(default_factory=dict)

REGISTRY = {
    "chimera_by_purity": MethodSpec(
        labeller_path="specb.compute.labelling:chimera_by_purity",
        encoder_path="specb.viz.encode:chimera_by_purity",
        required_params={"tsv_path"},  
    ),
}


def _resolve(path: str) -> Any:
    mod_path, sep, name = path.partition(":")
    if not sep:
        raise ValueError(f"Invalid path '{path}'. Expected 'package.module:attribute'")
    mod = importlib.import_module(mod_path)
    return getattr(mod, name)

def network_graph(c, threshold, method, **kwargs):
    G = nx.Graph()

    nodes = specb.io.specbsql.load_c2ls(c, path_d="cutoff_annotation.db", name_t="clusters")

    method_spec = REGISTRY.get(method)
    if method_spec is None:
        raise ValueError(f"Unknown method '{method}'. Available: {list(REGISTRY)}")

    missing = method_spec.required_params - set(kwargs)
    if missing:
        raise TypeError(f"Method '{method}' requires params: {sorted(missing)}")

    labeller = _resolve(method_spec.labeller_path)
    encoder = _resolve(method_spec.encoder_path)

    params = {**getattr(method_spec, "defaults", {}), **kwargs}

    dict_s2label = labeller(nodes, **params)
    dict_s2color = encoder(dict_s2label)
    
    for node in nodes:
        G.add_node(node)
    for node in nodes:
        for neighbor, dist in specb.io.archivesql.load_s2n(node, threshold).items():
            G.add_edge(node, neighbor)
    node_colors = [dict_s2color[node] for node in nodes ]
    pos = nx.kamada_kawai_layout(G)

    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=10, width=0.1)