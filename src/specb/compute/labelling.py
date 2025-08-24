# specb/compute/labelling.py
# given a list of nodes
# assign labels for downstream

from typing import Iterable
import specb.io as io

def chimera_by_purity(
    ls: Iterable[int],
    tsv_path: str,
    threshold: float = 0.5,
) -> dict[int, str]:

    dict_s2ms1purity = io.tsv.read_ms1purity(tsv_path)
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

def dbscan(
    ls: Iterable[int],
    c: int,
    path_d: str,
    name_t: str,
) -> dict[int, int]:
    
    dict_g2ls = io.specbsql.load_groups(c, path_d, name_t)
    
    dict_s2g = {}
    for g in dict_g2ls:
        for s in dict_g2ls[g]:
            dict_s2g[s] = g

    dict_s2label = {}
    for s in ls:
        dict_s2label[s] = dict_s2g.get(s, -1)

    return dict_s2label

def msfragger(
    ls: Iterable[int],
    path_d: str,
    name_t:str,
) -> dict[int, str]:
    
    dict_s2a = io.archivesql.load_ls2a(ls, path_d, name_t)
    dict_s2label = dict_s2a

    return dict_s2label