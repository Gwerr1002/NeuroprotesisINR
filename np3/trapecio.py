import matplotlib.pyplot as plt

def getTrapecio(t_s, t_b, t_m, t_a, c_max):
    nps = int(t_s/t_a) #numero de pulsos de subida
    npm = int(t_m/t_a) #numero de pulsos meseta
    npb = int(t_b/t_a) #nuero de pulsos bajada
    p_s = c_max*.9/nps #proporción de subida
    p_b = c_max*.9/npb #proporcion de bajada
    subida = [int(n*p_s) for n in range(1,nps+1)]
    meseta = [int(c_max) for n in range(npm)]
    bajada = [int(n*p_b) for n in range(npb,0,-1)]
    trapecio = subida+meseta+bajada
    t = [i*t_a for i in range(len(trapecio))]
    return t,trapecio


if __name__ == "__main__":
    #t, prueba = getTrapecio(100,100,200,10,20,100)
    t, prueba = getTrapecio(300,300,400,10,10)
    print(prueba)
    plt.stem(t,prueba)
    plt.show()