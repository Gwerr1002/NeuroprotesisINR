"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

Aquí solo se define el metodo para el cálculo del trapecio

"""
from numpy import array
def getTrapecio(t_s, t_b, t_m, msi, c_max):
    '''
    Calcula el vector de corrientes de una secuencia de una modulación trapezoidal
    con los parámetros dados

    Parameters
    ----------
    t_s: int
        tiempo de subida, debe ser indicado en ms

    t_b: int
        tiempo de bajada, debe ser indicado en ms
    
    t_m: int
        tiempo de meseta, debe ser indicado en ms
    
    msi: int
        Main Stimulation Interval

    c_max: int 
        corriente máxima, es la corriente de meseta
    
    Returns
    -------
    t: list
        Es el vector de tiempo para graficar el vector de trapecio
    trapecio: list
        Es el vector que contiene las corrientes del trapecio

    '''
    #División de los intervalos de subida y bajada en un numero definido
    nps = int(t_s/msi) #numero de pulsos de subida
    npm = int(t_m/msi) #numero de pulsos meseta
    npb = int(t_b/msi) #nuero de pulsos bajada
    #Cálculo del paso entre los intervalos
    p_s = c_max*.9/nps #proporción de subida
    p_b = c_max*.9/npb #proporcion de bajada
    #Generación de la subida y bajada escalando las proporciones de acuerdo al
    #numero de muestra
    subida = [int(n*p_s) for n in range(1,nps+1)]
    meseta = [int(c_max) for n in range(npm)]
    bajada = [int(n*p_b) for n in range(npb,0,-1)]
    trapecio = subida+meseta+bajada
    #vector de tiempo para graficar y observar el trapecio
    t = [i*msi for i in range(len(trapecio))]
    return array(t),trapecio


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    #t, prueba = getTrapecio(100,100,100,20,10)
    t, prueba = getTrapecio(100,100,100,10,15)
    print(prueba)
    plt.stem(t,prueba)
    plt.show()