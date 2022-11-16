from controlStim import CntrlStim
from trapecio import getTrapecio
import numpy as np
import matplotlib.pyplot as plt

msi = 20
pw = 300
canales = (6,7)

#ts=100, tb=100, tm=300, msi=20, max_current=20
t,v1 = getTrapecio(200,200,300,msi,20)
#ts=100, tb=100, tm=300, msi=20, max_current=10
t,v2 = getTrapecio(200, 200, 200, msi, 10)

v = []
i = 0
j = 0
traslape = 20
TOT= len(v1)+len(v2)
while len(v) != TOT:
    if i<traslape:
        v.append((pw,msi,v1[i],canales[0]))
        i += 1
    elif i>=traslape and i<len(v1):
        v.append((pw,msi/2,v2[j],canales[1]))
        j += 1
        v.append((pw,msi/2,v1[i],canales[0]))
        i += 1
    else:
        v.append((pw,msi,v2[j],canales[1]))
        j += 1

t1 = []
for i,a in enumerate(v):
    if a[-1] == 6:
        if a[1] == msi:
            t1.append(i*msi)
        else:
            t1.append(t1[-1]+msi)

c1 = [c for _,msi,c,canal in v if canal == 6]

t2=[]
aux = t1[traslape-1]+msi/2
for a in v:
    if a[-1] == 7:
        t2.append(aux+msi)
        aux = t2[-1]

c2 = [c for _,msi,c,canal in v if canal == 7]

if __name__ == '__main__':
    prueba = CntrlStim()
    for _ in range(10):
        prueba.sendSignal(v)
    prueba.exitStim()
    '''
    plt.step(t1,c1)
    plt.step(t2,c2)
    plt.show()
    '''
