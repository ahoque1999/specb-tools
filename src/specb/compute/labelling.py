# given a list of nodes
# assign labels for downstream

from typing import Iterable
from specb.io.tsv import read_ms1purity

def chimera_by_purity(
    ls: Iterable[int],
    tsv_path: str,
    threshold: float = 0.5,
) -> dict[int, str]:

    dict_s2ms1purity = read_ms1purity(tsv_path)
    dict_s2label: dict[int, str] = {}
    for s in ls:
        p = dict_s2ms1purity.get(s)
        if p is None:
            dict_s2label[s] = "unknown"
        elif p < threshold:
            dict_s2label[s] = "chimeric"
        else:
            dict_s2label[s] = "non-chimeric"
    return dict_s2label