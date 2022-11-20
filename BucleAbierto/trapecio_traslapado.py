from controlStim import CntrlStim
from trapecio import getTrapecio
from numpy import where

def getTrapecio_traslapado(t_s1,t_b1,t_m1,cmax1,t_s2,t_b2,t_m2,cmax2,t_traslape,pw,msi,canales = (6,7)):
    t, v1 = getTrapecio(t_s1,t_b1,t_m1,msi,cmax1)
    _, v2 = getTrapecio(t_s2,t_b2,t_m2,msi,cmax2)
    v,i,j = [],0,0
    traslape=where(t<=t_traslape)[0][-1] #Muestra en la cual se traslapa (aproximado acorde con msi y t_traslape)
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
    #
    return v,traslape

def getgraf_trapecio_traslapado(v,msi,traslape):
    t1,t2 = [],[]
    for i,a in enumerate(v):
        if a[-1] == 6:
            if a[1] == msi:
                t1.append(i*msi)
            else:
                t1.append(t1[-1]+msi)
    #
    c1 = [c for _,msi,c,canal in v if canal == 6]
    #
    aux = t1[traslape-1]+msi/2
    for a in v:
        if a[-1] == 7:
            t2.append(aux+msi)
            aux = t2[-1]
    #
    c2 = [c for _,msi,c,canal in v if canal == 7]
    return (t1,c1), (t2,c2)

if __name__ == '__main__':
<<<<<<< Updated upstream
    prueba = CntrlStim()
    for _ in range(10):
        prueba.sendSignal(v)
    prueba.exitStim()
    
    plt.step(t1,c1)
    plt.step(t2,c2)
    plt.show()
    
=======
    import matplotlib.pyplot as plt
    msi = 20
    pw = 300
    t_traslape = 200
    v,traslape = getTrapecio_traslapado(100,100,200,20,200,200,300,15,t_traslape,pw,msi)
    (t1,c1),(t2,c2)=getgraf_trapecio_traslapado(v,msi,traslape)
    plt.step(t1,c1)
    plt.step(t2,c2)
    plt.show()
>>>>>>> Stashed changes
