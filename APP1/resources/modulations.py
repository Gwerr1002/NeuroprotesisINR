from numpy import sin,pi,linspace, where, array, dstack, ones,zeros,append,flip
from from_file import save

def sinAMP(T,pw,msi,c_max,canal):
    """
    T: en millisegundos
    """
    w = 2*pi*T #El periodo en este caso es la duracion de una cresta en ms
    N = int(T/msi)
    t = linspace(0,T,N)
    x = c_max*sin(w*t)
    return [(pw,msi,int(i),canal) if i>=0 else (pw,msi,0,canal) for i in x]

def sinFREC(f,msi_max, pw, corriente, canal,N):
    '''
    msi_max: debe ser un número a partir de 10 
    '''
    w = 2*pi*f
    t = linspace(0,1/(f*4),int(N/4))
    x = (msi_max-11)*sin(w*t)+11 #El mínimo debe ser 11 ms
    x = append(flip(x),x)
    x = append(x,10*ones(int(N/2)))
    corrientes = array([corriente if msi > 10 else 0 for msi in x])
    zip = dstack((x,corrientes))[0]
    return [(pw,int(msi),int(c),canal) for msi,c in zip]

def sinPW(f,msi,pw_max,corriente,canal,N):
    """
    pw_max: debe ser un número entero mas grande que 0
    """
    w = 2*pi*f
    t = linspace(0,1/(f*2),int(N/2))
    x = (pw_max+1)*sin(w*t)+1 #Establecer un mínimo de 1 ns
    x = append(x,zeros(int(N/2)))
    corrientes = array([corriente if pw > 0 else 0 for pw in x])
    zip = dstack((x,corrientes))[0]
    return [(int(pw),msi,int(c),canal) for pw,c in zip]

if __name__ == "__main__":
    d = {
        "Modulación en Amplitud Sin": sinAMP(1000,400,10,20,7),
        "Modulación en frecuencia Sin": sinFREC(1,50,400,20,7,60),
        "Modulación del ancho de pulso": sinPW(.5,10,400,20,7,100),
        "Aplicación en dos canales": (sinAMP(1000,400,10,20,7)+sinAMP(1000,400,10,15,6)),
        }
    for key in d:
        print(key+":")
        print(d[key])
    save("./examples_usrmode","ejemplo.json",d)
    save("./examples_usrmode","ejemplo.npy", d)
    save("./examples_usrmode","ejemplo.mat", d)