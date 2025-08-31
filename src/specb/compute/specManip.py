import sqlite3
import pandas as pd
import numpy as np
from pyteomics import mzxml
import xml.etree.ElementTree as ET
import pyopenms as oms
import scipy

def fetch_spec_details(db_path, specid):
    """
    Fetches details for a given spec ID from the database.

    Parameters:
        db_path (str): Path to the SQLite database file.
        specid (int): The specific ID to look up.

    Returns:
        tuple: A tuple containing (specid, file path, scan number)
    """

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Fetch FILEID from the GROUNDTRUTH table
        cursor.execute("SELECT FILEID, SCAN FROM GROUNDTRUTH WHERE ID = ?", (specid,))
        result = cursor.fetchone()
        if not result:
            print("No data found for specID:", specid)
            return None

        file_id, scan_number = result

        # Fetch FILENAME using FILEID from the SPECFILES table
        cursor.execute("SELECT FILENAME FROM SPECFILES WHERE FILE_ID = ?", (file_id,))
        file_name_result = cursor.fetchone()
        if not file_name_result:
            print("No filename found for FILEID:", file_id)
            return None

        file_path = file_name_result[0]

        return (specid, file_path, scan_number)

    except sqlite3.Error as e:
        print("Database error:", e)
        return None

    finally:
        # Close the connection to the database
        cursor.close()
        conn.close()


def get_spec_details_df(specids, db_path='/data/ayman/SpecArchive/archive.sqlite3db'):
    if type(specids) == str:
        specids = list(map(int, specids.split(',')))
    spec_details = []
    for specid in specids:
        details = fetch_spec_details(db_path, specid)
        if details:
            spec_details.append(details)
        else:
            print("Data not found for SpecID: " + specid)
    return pd.DataFrame(spec_details, columns=['SpecID', 'FilePath', 'ScanNumber'])

CUTOFF_ANNOTATION = sqlite3.connect("/data/ayman/SpecArchive/cutoff_annotation.db")
CUTOFF_ANNOTATION_CUR = CUTOFF_ANNOTATION.cursor()

def getNodesFromGroupID(group_id):
    CUTOFF_ANNOTATION_CUR.execute('SELECT group_key, nodes FROM dbscan_method1_groups WHERE group_key = "' + group_id + '"')
    group_keys = CUTOFF_ANNOTATION_CUR.fetchall()
    
    return group_keys[0][1].split(",")

def getMajorityAnnotaitonFromGroupID(group_id):
    CUTOFF_ANNOTATION_CUR.execute('SELECT group_key, majority_annotation, majority_percentage FROM dbscan_method1_groups WHERE group_key = "' + group_id + '"')
    group_keys = CUTOFF_ANNOTATION_CUR.fetchall()
    
    return group_keys[0][1:]


getmzdict_memoization = {}

def getmzdict(file, scannumber):
    query = (file, str(scannumber))
    if query in getmzdict_memoization.keys():
        return getmzdict_memoization[query]
    with mzxml.MzXML(file) as reader:
        ret = reader.get_by_id(str(scannumber), "num")
    getmzdict_memoization[query] = ret
    return ret

def getVector(file, scannumber, MIN, MAX, BINWIDTH):
    ret=[0 for _ in range(len(np.arange(MIN, MAX, BINWIDTH)))]
    dic=getmzdict(file, scannumber)
    for i, each in enumerate(dic["m/z array"]):
        ret[int((each-MIN)/BINWIDTH)]=dic["intensity array"][i]
    return ret

def getUnitVector(file, scannumber, MIN, MAX, BINWIDTH):
    ret=np.array(getVector(file, scannumber, MIN, MAX, BINWIDTH))
    ret/=np.linalg.norm(ret)
    return ret


import re

def removeModifications(peptideSequence):
    return re.sub(r"\(.*?\)", "", peptideSequence)

def getType(bridge, other_annotations):
    UNKNOWN = "UNKNOWN"
    all_annotations = [bridge] + other_annotations
    n_annotations = len(set(all_annotations))
    if n_annotations == 1:
        ret_string_list = list("AAA")
    elif n_annotations == 2:
        if other_annotations[0] == other_annotations[1]:
            ret_string_list = list("ABA")
        else:
            ret_string_list = list("AAB")
    else: # n_annotations == 3
        ret_string_list = list("ABC")
    if bridge == UNKNOWN:
        ret_string_list[1] = "U"
    unknown_count = other_annotations.count(UNKNOWN)
    if unknown_count == 1:
        ret_string_list[2] = "U"
    elif unknown_count == 2:
        ret_string_list[0] = ret_string_list[2] = "U"
    current_letter = "A"
    prev_letters = {}
    for i, each in enumerate(ret_string_list):
        if each in ["A", "B", "C"]:
            if each in prev_letters.keys():
                ret_string_list[i] = prev_letters[each]
            else:
                prev_letters[each] = current_letter
                ret_string_list[i] = current_letter
                current_letter = chr(ord(current_letter) + 1)
    Type = "".join(ret_string_list)
    if "(" in "".join(all_annotations) and Type == "AAB":
        NewType = getType(removeModifications(bridge), [removeModifications(each) for each in other_annotations])
        if NewType == "AAA":
            Type = "AAB (modification)"
    return Type


#ms1

# Get ms1 scan number, ms1 center m/z value, window width
def getPrecursorInfo(mzxml, scannumber):
    scannumber = str(scannumber)
    tree = ET.parse(mzxml)
    root = tree.getroot()
    for i, child in enumerate(root[0]):
        if "}scan" in child.tag and child.attrib["num"] == scannumber:
            return (int(child[0].attrib["precursorScanNum"]),
                    float(child[0].text),
                    float(child[0].attrib["windowWideness"])
                   )

def getSpectraFromScanNumbers(mzxml, scannumbers):
    if type(scannumbers) == int or type(scannumbers) == str:
        scannumbers = [scannumbers]
    scannumbers = [str(each) for each in scannumbers]
    exp = oms.MSExperiment()
    oms.MzXMLFile().load(mzxml, exp)

    spectra = []
    for scannumber in scannumbers:
        flag = False
        for each in exp:
            if each.getNativeID()[len("scan="):] == scannumber:
                flag = True
                break
        if flag:
            spectra.append(each)
        else:
            raise Exception("Scan Number " + scannumber + " Not Fount!")
    return spectra

def getPurityScore(mzxml, ms2ScanNumber):
    ms1ScanNumber, precursorCenterMZValue, windowWideness = getPrecursorInfo(mzxml, ms2ScanNumber)
    ms2Spectrum, ms1Spectrum = getSpectraFromScanNumbers(mzxml, (ms2ScanNumber, ms1ScanNumber))
    pre = ms2Spectrum.getPrecursors()[0]
    purity_score = oms.PrecursorPurity().computePrecursorPurity(ms1Spectrum, pre, 10, True)
    return (purity_score.total_intensity,
            purity_score.target_intensity,
            purity_score.signal_proportion,
            purity_score.target_peak_count,
            purity_score.interfering_peak_count
           )

# temp
ms1_db_path = "/data3/ayman/specb-tools/src/specb/compute/ms1_database.tsv"
MS1_DATABASE = pd.read_table(ms1_db_path, index_col=0)

def getPurityScoreFromNode(node, update=False):

    global MS1_DATABASE
    
    try:
        return MS1_DATABASE["signal_proportion"][int(node)]
    except KeyError:
        filePathAndScanNumber = get_spec_details_df([str(node)])
        try:
            result = getPurityScore(filePathAndScanNumber["FilePath"][0], filePathAndScanNumber["ScanNumber"][0])
            if update:
                MS1_DATABASE.loc[node] = result
                MS1_DATABASE.to_csv(ms1_db_path, sep="\t")
            return result[2]
        except KeyError:
            return None
        

def getUnitVectorByNode(node, MIN, MAX, BINWIDTH):
    spec_details = get_spec_details_df([node])
    return getUnitVector(spec_details.iloc[0]["FilePath"], spec_details.iloc[0]["ScanNumber"], MIN, MAX, BINWIDTH)

def getGroupFromNode(node):
    CUTOFF_ANNOTATION_CUR.execute('SELECT group_key FROM dbscan_method1_groups WHERE nodes LIKE "' + str(node) + '" OR nodes LIKE "%,' + str(node) + ',%" OR nodes LIKE "' + str(node) + ',%" OR nodes LIKE "%,' + str(node) + '"')
    group_keys = CUTOFF_ANNOTATION_CUR.fetchall()
    return [group[0] for group in group_keys]

def recruitNeighboringGroups(group):
    CUTOFF_ANNOTATION_CUR.execute('SELECT group_key FROM dbscan_method1_groups WHERE group_key LIKE "' + group.split("_")[0] + '\_%" ESCAPE "\\"')
    group_keys = CUTOFF_ANNOTATION_CUR.fetchall()
    groups = [group[0] for group in group_keys]
    return sorted(groups, key=lambda group: int(group.split("_")[1]))

def getLCResults(A, node, neighboring_groups, MIN, MAX, BINWIDTH):
    targetVector = getUnitVectorByNode(int(node), MIN, MAX, BINWIDTH)
    nnlsResult = scipy.optimize.nnls(A, targetVector)
    approximatedVector = np.matmul(A, nnlsResult[0])
    percentageError = nnlsResult[1] / np.linalg.norm(targetVector)
    cosSimilarity = np.sum(approximatedVector * targetVector) / np.linalg.norm(approximatedVector) / np.linalg.norm(targetVector)
    entropyScore = 1 - scipy.stats.entropy(nnlsResult[0]) / scipy.stats.entropy([1] * len(neighboring_groups))
    return [str(nnlsResult[0].tolist()), entropyScore, percentageError, cosSimilarity]

def normalize(vector):
    return np.array(vector) / np.linalg.norm(vector)

def getLCEntropyScoreByNode(node, neighboring_groups=[], update=False, database="/data/carlos/LC_database/LC_database.tsv"):
    groups_node = getGroupFromNode(node)
    if len(groups_node) > 1:
        raise Exception("Node belongs to more than 1 group")

    defined_neighboring_group = (neighboring_groups != [])
    
    if defined_neighboring_group:
        neighboring_groups = sorted(neighboring_groups, key=lambda group: int(group.split("_")[1]))
    else:
        neighboring_groups = recruitNeighboringGroups(groups_node[0])
    
    n_groups = len(neighboring_groups)
    
    try:
        database_df = pd.read_table(database)
        return database_df[(database_df["SpecID"] == node) & (database_df["NeighboringGroups"] == str(neighboring_groups))].iloc[0]["EntropyScore"]
    except: # file does not exist or database does not have info on the node
        pass
    

    fetchedIDs = [getNodesFromGroupID(group) for group in neighboring_groups]
    spec_details_dfs = [get_spec_details_df(IDs) for IDs in fetchedIDs]
    
    mzarray = []
    for df in spec_details_dfs + [get_spec_details_df([node])]: # handle case when node is not within neighboring_groups
        for each in df.iloc:
            mzarray += getmzdict(each["FilePath"], each["ScanNumber"])["m/z array"].tolist()
    
    MIN = np.floor(min(mzarray)).astype(int)
    MAX = np.ceil(max(mzarray)).astype(int)
    BINWIDTH = 0.02
    
    vectors=[[] for i in range(n_groups)]
    
    for i, df in enumerate(spec_details_dfs):
        for each in df.iloc:
            vectors[i].append(getUnitVector(each["FilePath"], each["ScanNumber"], MIN, MAX, BINWIDTH))
    
    for i in range(n_groups):
        vectors[i] = normalize(np.mean(vectors[i], axis=0))
    
    A = np.array(vectors).transpose()
    
    try:
        result_df = database_df
    except NameError: # database file does not exist
        result_df = pd.DataFrame(columns=["SpecID", "Group", "NeighboringGroups", "Coefficients", "EntropyScore", "PercentageError", "CosSimilarity"])
    if update:
        for i, currentGroupIDs in enumerate(fetchedIDs):
            for current_node in currentGroupIDs:
                if len(result_df[(result_df["SpecID"] == int(current_node)) & (result_df["NeighboringGroups"] == str(neighboring_groups))]) == 0:
                    newdata = [int(current_node), neighboring_groups[i], str(neighboring_groups)] + getLCResults(A, current_node, neighboring_groups, MIN, MAX, BINWIDTH)
                    newrow = pd.DataFrame(columns=result_df.columns.tolist(), data=[newdata])
                    result_df = pd.concat([result_df, newrow], axis=0)
        while True:
            try:
                ret = result_df[(result_df["SpecID"] == node) & (result_df["NeighboringGroups"] == str(neighboring_groups))].iloc[0]["EntropyScore"]
                break
            except IndexError:
                newdata = [node, groups_node[0], str(neighboring_groups)] + getLCResults(A, node, neighboring_groups, MIN, MAX, BINWIDTH)
                newrow = pd.DataFrame(columns=result_df.columns.tolist(), data=[newdata])
                result_df = pd.concat([result_df, newrow], axis=0)
        result_df.to_csv(database, sep="\t", index=False)
        return ret
    else:
        return getLCResults(A, node, neighboring_groups, MIN, MAX, BINWIDTH)[1]
