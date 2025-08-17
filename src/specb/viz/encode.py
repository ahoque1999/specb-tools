# given dict of nodes and their labels
# assign colors

def chimera_by_purity(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_label2color = {
        "chimeric": "red",
        "non-chimeric": "blue",
        "unknown": "black"
    }
    
    dict_s2color: dict[int, str] = {}
    for id_s, label in dict_s2label.items():
        dict_s2color[id_s] = dict_label2color.get(label, "yellow")
    return dict_s2color