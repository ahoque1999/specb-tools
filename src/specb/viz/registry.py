# specb/viz/registry.py

import importlib
from typing import Any
from dataclasses import dataclass, field


@dataclass
class MethodSpec:
    labeller_path: str              
    encoder_path: str              
    required_params: set[str] = field(default_factory=set)

REGISTRY = {
    "chimera_by_purity": MethodSpec(
        labeller_path="specb.compute.labelling:chimera_by_purity",
        encoder_path="specb.viz.encode:chimera_by_purity",
        required_params={"tsv_path"},  
    ),
    "dbscan": MethodSpec(
        labeller_path="specb.compute.labelling:dbscan",
        encoder_path="specb.viz.encode:dbscan",
        required_params={"path_d", "name_t"},
    ),
    "msfragger": MethodSpec(
        labeller_path="specb.compute.labelling:msfragger",
        encoder_path="specb.viz.encode:msfragger",
        required_params={"path_d", "name_t"},
    ),
}

def _resolve(path: str) -> Any:
    mod_path, sep, name = path.partition(":")
    if not sep:
        raise ValueError(f"Invalid path '{path}'. Expected 'package.module:attribute'")
    mod = importlib.import_module(mod_path)
    return getattr(mod, name)
