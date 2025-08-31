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
    #temp
    "chimera_by_purity_temp": MethodSpec(
        labeller_path="specb.compute.labelling:chimera_by_purity_temp",
        encoder_path="specb.viz.encode:chimera_by_purity_temp",
        required_params=set(),  
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
    "boundary": MethodSpec(
        labeller_path = "specb.compute.labelling:boundary",
        encoder_path = "specb.viz.encode:boundary",
        required_params = {"path_d_archive", "path_d_specb", "name_t_groundtruth", "name_t_groups"},
    ),
    "lc": MethodSpec(
        labeller_path = "specb.compute.labelling:lc",
        encoder_path = "specb.viz.encode:lc",
        required_params = set(),
    )
}

def _resolve(path: str) -> Any:
    mod_path, sep, name = path.partition(":")
    if not sep:
        raise ValueError(f"Invalid path '{path}'. Expected 'package.module:attribute'")
    mod = importlib.import_module(mod_path)
    return getattr(mod, name)
