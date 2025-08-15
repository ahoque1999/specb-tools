import pandas as pd

def read_ms1purity(path_csv: str) -> dict[int, float]:
    df = pd.read_csv(path_csv, sep='\t', header=None, names=["id_s", "ms1purity"])

    df["id_s"] = pd.to_numeric(df["id_s"], errors="coerce")
    df["ms1purity"] = pd.to_numeric(df["ms1purity"], errors="coerce")
    df = df.dropna(subset=["id_s", "ms1purity"])

    df = df.drop_duplicates(subset=["id_s"], keep="last")

    series = df.set_index("id_s")["ms1purity"]
    
    return {int(k): float(v) for k, v in series.items()}