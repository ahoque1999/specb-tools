# specb-tools/src/specb/io/specb_read.py
from typing import List
import sqlite3

def load_c2ls(c: int, path_d: str='specbase.specbsql', name_t: str='clusters') -> List[int]:
    if not name_t.isidentifier():
        raise ValueError(f"Invalid table name: {name_t!r}")
    
    sql = (
        f'''
        SELECT nodes
        FROM {name_t}
        WHERE cluster_id = ?
        LIMIT 1
        '''
    )

    with sqlite3.connect(path_d) as conn:
        cur = conn.execute(sql, (c,))
        row = cur.fetchone()
    
    if not row or row[0] is None:
        return []
    
    raw = str(row[0])
    if not raw.strip():
        return []

    try:
        spectra = [int(tok.strip()) for tok in raw.split(',') if tok.strip()]
    except ValueError as exc:
        raise ValueError(f"Malformed nodes list for cluster_id={c}: {raw!r}") from exc

    return spectra


def load_groups(c: int, path_d: str='specbase.specbsql', name_t: str='groups') -> dict[int, List[int]]:
    if not name_t.isidentifier():
        raise ValueError(f"Invalid table name: {name_t!r}")    
    
    sql = (
        f'''
        SELECT group_key, nodes
        FROM {name_t}
        WHERE cluster_id = ?
        '''
    )

    with sqlite3.connect(path_d) as conn:
        cur = conn.execute(sql, (c,))
        rows = cur.fetchall()
    
    groups = {}
    for row in rows:
        group_key, nodes = row

        try:
            group_key = group_key.split('_')
            if len(group_key) != 2:
                continue
            group = int(group_key[1])
            
            if nodes is None or nodes == '':
                nodes = []
            else:
                nodes = list(map(int, nodes.split(',')))
            
            groups[group] = nodes

        except (ValueError, AttributeError):
            continue

        
    return groups
    
