# specb/compute/annotation.py

import pyteomics.mass as std_mass

def gen_s(peptide: str, nterm: float, modification: str) -> str:
    
    amino_acids = list(peptide)
    modifications = {}
    mod_names = {}

    if modification != "UNMODIFIED":
        mods = modification.strip("|").split("|")
        for mod in mods:
            if mod:
                mod_val, mod_pos_str = mod.split("@")
                mod_pos = int(mod_pos_str) - 1
                del_mass = float(mod_val) - std_mass.std_aa_mass[amino_acids[mod_pos]]
                modifications[mod_pos] = del_mass
    
    if nterm != 0.0:
        if 0 in modifications:
            modifications[0] += nterm
        else:
            modifications[0] = nterm
        
    for pos, del_mass in modifications.items():
        if del_mass > 0:
            mod_name = f"+{del_mass:.4f}"
        else:
            mod_name = f"-{del_mass:.4f}"
        mod_names[pos] = mod_name
        amino_acids[pos] = f"{amino_acids[pos]}({mod_name})"

    modified_sequence = ''.join(amino_acids)

    return modified_sequence


def gen_a(peptide: str, nterm: float, modification: str, charge: InterruptedError) -> str:
    modified_sequence = gen_s(peptide, nterm, modification)

    return f"{modified_sequence}/{charge}"
