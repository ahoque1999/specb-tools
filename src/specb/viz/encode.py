# specb/viz/encode.py

# given dict of nodes and their labels
# assign colors

def chimera_by_purity(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_label2color = {
        "chimeric": "red",
        "non-chimeric": "blue",
        "unknown": "black"
    }
    
    dict_s2color: dict[int, str] = {}
    for s, label in dict_s2label.items():
        dict_s2color[s] = dict_label2color.get(label, "yellow")
    return dict_s2color

# temp
def chimera_by_purity_temp(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_label2color = {
        "chimeric": "red",
        "non-chimeric": "black",
        "unknown": "blue"
    }
    
    dict_s2color: dict[int, str] = {}
    for s, label in dict_s2label.items():
        dict_s2color[s] = dict_label2color.get(label, "yellow")
    return dict_s2color

def dbscan(dict_s2label: dict[int, int]) -> dict[int, str]:
    dict_label2color = {
        -1: "black",
        0: "red",
        1: "blue",
        2: "green"
    }

    dict_s2color: dict[int, str] = {}
    for s, label in dict_s2label.items():
        dict_s2color[s] = dict_label2color.get(label, "yellow")
    return dict_s2color


def msfragger(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_number2color = {
        -1: "black",
        0: "red",
        1: "blue",
        2: "green"
    }

    labels = [label for label in dict_s2label.values() if label != "UNKNOWN"]
    unique_labels = set(labels)
    dict_label2number = {label: i for i, label in enumerate(unique_labels)}
    dict_label2number["UNKNOWN"] = -1

    dict_s2color: dict[int, str] = {}
    for s, label in dict_s2label.items():
        dict_s2color[s] = dict_number2color[dict_label2number[label]]
    return dict_s2color


def boundary(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_label2color = {
        "boundary": "red",
        "non-boundary": "black",
        "pseudo-boundary": "blue",
    }

    dict_s2color: dict[int, str] = {}
    for s, label in dict_s2label.items():
        dict_s2color[s] = dict_label2color.get(label, "yellow")
    return dict_s2color

def lc(dict_s2label: dict[int, str]) -> dict[int, str]:
    dict_label2color = {
        "chimeric": "red",
        "non-chimeric": "blue",
    }

    dict_s2color: dict[int, str]= {}
    for s, label in dict_s2label.items():
        dict_s2color[s] =  dict_label2color.get(label, "yellow")
    return dict_s2color