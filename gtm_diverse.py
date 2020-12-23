import base64
from io import BytesIO
from rdkit import SimDivFilters
from rdkit.Chem import ForwardSDMolSupplier, rdMolDescriptors


def gtm_diverse(files, count):
    molecules = []
    molecules_fps = []
    for content in files:
        data = content.encode("utf8").split(b";base64,")[1]
        suppl = ForwardSDMolSupplier(BytesIO(base64.decodebytes(data)))
        for mol in suppl:
            try:
                molecules_fps.append(rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2))
                molecules.append(mol)
            except:
                pass

    if len(molecules) <= count:
        return molecules
    
    mmp = SimDivFilters.MaxMinPicker()
    picks = mmp.LazyBitVectorPick(molecules_fps, len(molecules_fps), count)
    return [molecules[i] for i in picks]
