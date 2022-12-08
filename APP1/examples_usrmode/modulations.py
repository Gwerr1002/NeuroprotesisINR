from numpy import sin,pi,linspace
from ..resources.from_file import save

def sin(T,pw,msi,c_max,canal):
    w = pi/T #El periodo en este caso es la duracion de una cresta en ms
    N = int(T/msi)
    t = linspace(0,T,N)
    x = c_max*sin(w*t)
    return [(pw,msi,int(i),canal) for i in x]