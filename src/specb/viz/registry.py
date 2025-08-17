# specb/viz/registry.py
from dataclasses import dataclass, field

@dataclass
class MethodSpec:
    labeller_path: str              
    encoder_path: str              
    required_params: set[str] = field(default_factory=set)
    defaults: dict = field(default_factory=dict)

REGISTRY = {
    "chimera_by_purity": MethodSpec(
        labeller_path="specb.compute.labelling:chimera_by_purity",
        encoder_path="specb.viz.encode:chimera_encoder",
        required_params={"tsv_path"},  
    ),
}