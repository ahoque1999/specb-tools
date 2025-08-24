# specb/io/archivesql.py
# load from archive.sqlite3db

import sqlite3
import specb.compute.annotation as annotation

def load_s2n(s: int, threshold:float, path_d: str='archive.sqlite3db', name_t: str='groundtruth') -> dict[int, float]:
    if not name_t.isidentifier():
        raise ValueError(f"Invalid table name: {name_t!r}")
    
    sql = (
        f'''
        SELECT NEIGHBOR
        FROM {name_t}
        WHERE ID = ?
        LIMIT 1
        '''
    )

    with sqlite3.connect(path_d) as conn:
        cur = conn.execute(sql, (s,))
        row = cur.fetchone()
    
    if not row or row[0] is None:
        return {}

    d = {}
    raw = str(row[0])

    try:
        for link in raw.split(';'):
            link = link.strip()
            if not link:
                continue
            dist, node = link.split('@')
            node = int(node)
            if node == s:
                continue
            dist = float(dist)
            if dist > threshold:
                continue
            d[node] = dist
    except ValueError as exc:
        raise ValueError(f"Malformed neighbors for ID={s}: {raw!r}") from exc

    return d

def load_ls2a(ls: list[int], path_d: str='archive.sqlite3db', name_t: str='GROUNDTRUTH') ->dict[int, str]:
    if not name_t.isidentifier():
        raise ValueError(f"Invalid table name: {name_t!r}")

    sql = (
        f'''
        SELECT PEPTIDE, NTERM, MODIFICATION, CHARGE, SIGNIFICANCE
        FROM {name_t}
        WHERE ID = ?
        LIMIT 1
        '''
    )

    res = {}

    with sqlite3.connect(path_d) as conn:
        cur = conn.cursor()
        for s in ls:
            cur.execute(sql, (s,))
            row = cur.fetchone()
            if row is None:
                res[s] = "UNKNOWN"
                continue
            peptide, nterm, modification, charge, significance = row
            if significance == 0:
                res[s] = "UNKNOWN"
                continue
            res[s] = annotation.gen_a(peptide, nterm, modification, charge)

    return res