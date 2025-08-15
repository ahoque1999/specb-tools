# specb-tools/src/specb/io/specb_read.py
from __future__ import annotations
from typing import List
import sqlite3

def load_c2ls(id_c: int, path_d: str='specbase.sql', name_t: str='clusters') -> List[int]:
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
        cur = conn.execute(sql, (id_c,))
        row = cur.fetchone
    
    if not row or row[0] is None:
        return []
    
    raw = str(row[0])
    if not raw.strip():
        return []

    try:
        nodes = [int(tok.strip()) for tok in raw.split(',') if tok.strip()]
    except ValueError as exc:
        raise ValueError(f"Malformed nodes list for cluster_id={id_c}: {raw!r}") from exc

    return nodes