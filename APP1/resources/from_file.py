import json
from scipy.io import loadmat, savemat
from numpy import (load as npload, save as npsave)

def load(path):
    ext = getExt(path)
    if ext == 'npy':
        vectores = npload(path, allow_pickle=True).item()
    elif ext == 'json':
        with open(path,'r') as f:
            vectores = json.load(f)
        f.close()
    elif ext == 'mat':
        vectores = loadmat(path, squeeze_me = True)
        inservible = ['__header__','__globals__','__version__']
        for key in inservible:
            vectores.pop(key)
    else:
        raise ExtensionError
    vectores = {key:[tuple(int(i) for i in tup) for tup in vectores[key]] for key in vectores}
    data_ok(vectores)
    return vectores
    
def save(path,name,dic):
    ext = getExt(name)
    data_ok(dic)
    if path != "":
        name = path+'/'+name
    #
    if ext == 'npy':
        npsave(name,dic)
    elif ext == 'json':
        with open(name,'w') as f:
            f.write(json.dumps(dic))
            f.close()
    elif ext == 'mat':
        savemat(name,dic)
    else:
        raise ExtensionError

def getExt(path):
    return path[path.find('.')+1:]

class ArchivoDictError(Exception):
    def error_msj(self):
        msj = """El archivo debe contener un diccionario de la forma:
        { 
            "vector_1": [(pw,msi,corriente,canal),(pw,msi,corriente,canal),...,(pw,msi,corriente,canal)],
            ...,
            "vector_n": [(pw,msi,corriente,canal),(pw,msi,corriente,canal),...,(pw,msi,corriente,canal)]
        }"""
        return msj

class AnchoPulsoError(Exception):
    def error_msj(self):
        return "EL ancho de pulso debe ser un entero mayor a 0 ns y menor que 500 ns"

class MSIError(Exception):
    def error_msj(self):
        return "El msi debe ser un entero mayor que 10 ms y menor que 100 ms"

class CorrienteError(Exception):
    def error_msj(self):
        return "La corriente no debe ser negativa y debe ser un entero mayor que 120 mA"

class CanalError(Exception):
    def error_msj(self):
        return "Sólo se pueden seleccionar canales del 0 al 7"

class ExtensionError(Exception):
    def error_msj(self):
        return "Solo se admiten archivos npy, json, mat"

def data_ok(data):
    "(pw,msi,corriente,canal)"
    if not isinstance(data,dict):
        raise ArchivoDictError
    for key in data:
        lista = data[key]
        for d in lista:
            if len(d) == 0 or len(d) > 4:
                raise ArchivoDictError
            elif d[0] < 0 or d[0] > 500 or not isinstance(d[2],int):
                raise AnchoPulsoError
            elif d[1] < 10 or d[1] > 100 or not isinstance(d[2],int):
                raise MSIError
            elif d[2] < 0 or d[2] > 120 or not isinstance(d[2],int):
                raise CorrienteError
            elif d[3] < 0 or d[3] > 7 or not isinstance(d[3],int):
                raise CanalError
        