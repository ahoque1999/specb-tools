# specb/compute/labelling.py
# given a list of nodes
# assign labels for downstream

from typing import Iterable
import specb.io as io
import specb.compute as compute
from tqdm import tqdm

# temporary labelling
def chimera_by_purity_temp(
    ls: Iterable[int],
    threshold: float = 0.7,
) -> dict[int, str]:


    dict_s2label: dict[int, str] = {}
    for s in ls:
        p = compute.specManip.getPurityScoreFromNode(s, True)
        if p is None:
            dict_s2label[s] = "unknown"
        elif p < threshold:
            dict_s2label[s] = "chimeric"
        else:
            dict_s2label[s] = "non-chimeric"
    return dict_s2label


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


def boundary(
        ls: Iterable[int],
        c: int,
        threshold_dist: float,
        path_d_archive: str,
        path_d_specb: str,
        name_t_groundtruth: str,
        name_t_groups:str,
) -> dict[int, str]:
    dict_s2group = dbscan(ls, c, path_d_specb, name_t_groups)
    dict_s2msfragger = msfragger(ls, path_d_archive, name_t_groundtruth)

    def _is_boundary(s, dict_s2group, dict_s2msfragger, threshold_dist):
        s_group = dict_s2group[s]
        s_msfragger = dict_s2msfragger[s]
        for neighbor, _ in io.archivesql.load_s2n(s, threshold_dist).items():
            n_group = dict_s2group.get(neighbor, -1)
            n_msfragger = dict_s2msfragger.get(neighbor, "UNKNOWN")
            
            if (s_group != n_group) or (s_msfragger != n_msfragger):
                return True
            # if (s_group != n_group):
            #     return True
        return False

    dict_s2label = {}
    boundary_set = set()
    for s in ls:
        if _is_boundary(s, dict_s2group, dict_s2msfragger, threshold_dist):
            dict_s2label[s] = "boundary"
            boundary_set.add(s)
            continue

    for s in ls:
        if s in boundary_set:
            continue
        for neighbor, _ in io.archivesql.load_s2n(s, threshold_dist).items():
            if neighbor in boundary_set:
                dict_s2label[s] = "pseudo-boundary"
                break
    
    for s in ls:
        if s not in dict_s2label:
            dict_s2label[s] = "non-boundary"

    return dict_s2label

def lc(
    ls: Iterable[int],
    lc_threshold: float = 0.5,
) -> dict[int, str]:
    
    pbar = tqdm(ls, desc="calculating the LC scores")
    dict_s2label = {}
    for s in pbar:
        pbar.set_postfix(spectrum=s)
        lc_score = compute.specManip.getLCEntropyScoreByNode(s)
        if lc_score < lc_threshold:
            dict_s2label[s] = "chimeric"
            continue
        dict_s2label[s] = "non-chimeric"
    return dict_s2label
