"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

"""

from controlStim import CntrlStim
from trapecio import getTrapecio
import time
from threading import Thread, Event
from playsound import playsound
from numpy import append, array

"""
Parámetros de la secuencia de estimulación.
    + candency: cadencia indicada en zancadas por minuto
    + duty_cycle: ciclo de trabajo de cada trapecio, 1 equivale al 100%
                en terminos del inverso de la cadencia
    + corriente_max1: corriente máxima del canal 1 del trapecio en milliamperes
    + corriente_max2: corriente máxima del canal 2 del trapecio en milliamperes
    + msi : Main Stimulation Interval, debe indicarse en millisegundos, el mínimo es de 8ms.
            Por motivos de la aplicación se debe cuidar que no supere el tiempo de WATCHDOG
            que es de 1200 ms
    + pulse_width: Ancho de pulso en microsegundos [0,500 us]
    + t_subida: El tiempo de subida que requiere el trapecio en millisegundos
    + t_bajada: Tiempo de bajada del trapecio en millisegundos
    + tiempo:  Es el tiempo total de la sesión en segundos. Se debe tomar en cuenta
    que este parámetro dado no será el tiempo exacto, ya que se hará un cálculo
    de cuantos trapecios son necesarios para cumplir con este tiempo aproximadamente.
"""

cadency = 30
dutycycle = .5
corriente_max_1 = 10 #canal 8
corriente_max_2 = 10 #canal 7
msi = 20
pulse_width = 400
t_subida = 100
t_bajada = 100
tiempo = 13.5 #En segundos

class open_loop():
    def __init__(self,tiempo, cadency, dutycycle, max_current1,max_current2,msi, pw,t_ascent, t_descent,channels = (6,7)):

        #canales del estimulador que se usaran
        self.channels = channels
        self.msi = msi
        #Calculos de los tiempos
        periodo_zancada = 60/cadency #en segundos
        apoyo = periodo_zancada*dutycycle
        balanceo = periodo_zancada*(1-dutycycle)
        t_meseta1 = apoyo*1e+3-(t_subida+t_bajada)
        t_meseta2 = balanceo*1e+3-(t_subida+t_bajada)
        #calculo del trapecio
        self.t1,self.v1 = getTrapecio(t_ascent,t_descent,t_meseta1,msi,max_current1)
        self.t2,self.v2 = getTrapecio(t_ascent,t_descent,t_meseta2,msi,max_current2)
        self.vector1=[(pw,msi,c,channels[0]) for c in self.v1] #se le pega el ancho de pulso en us
        self.vector2=[(pw,msi,c,channels[1]) for c in self.v2]

        #Numero de interaciones necesarias para cumplir con el tiempo dado
        self.N = int(round(tiempo/periodo_zancada))
        print(self.N)

        #Control del registro de datos (guardar secuencia de estimulación desde el inicio del programa)
        self.t0 = time.time() #inicio del programa
        self.tch1 = [] #guarda tiempos de estimulación del canal ch1
        self.tch2 = []

        #Ejecución del ciclo en un hilo distinto al del programa
        self.hilo = Thread(target=self.loop)
        self.end = Event()

        #inicializar la conexion con el estimulador y configuración
        self.c_stim = CntrlStim()

    def start(self):
        self.hilo.start()

    def stop(self):
        self.end.set()
        t1 = append(0,self.t1)
        t1 = append(t1,self.t1[-1]+self.msi)
        t2 = append(0,self.t2)
        t2 = append(t2,self.t2[-1]+self.msi)
        v1 = append(append(0,self.v1),0)
        v2 = append(append(0,self.v2),0)
        tch1_reg = [(t-self.t0) for t in self.tch1]
        tch2_reg = [(t-self.t0) for t in self.tch2]
        tch1 = array([0])
        c1 = tch1
        tch2 = array([0])
        c2 = tch2
        for i in tch1_reg:
            tch1 = append(tch1,t1/1000+i)
            c1 = append(c1,v1)
        for i in tch2_reg:
            tch2 = append(tch2,t2/1000+i)
            c2 = append(c2,v2)

        return (tch1,c1),(tch2,c2)

    def loop(self):
        for _ in range(self.N):
            Thread(target=playsound,args=("sin440.wav",)).start()
            self.tch1.append(time.time())
            self.c_stim.sendSignal(self.vector1)
            Thread(target=playsound,args=("sin880.wav",)).start()
            self.tch2.append(time.time())
            self.c_stim.sendSignal(self.vector2)
            if self.end.is_set():
                break
        self.c_stim.port.close()
        self.c_stim.exitStim()

    def rutina_wdg(self):
        self.c_stim.send_packet(self.c_stim.WATCHDOG)
        time.sleep(0.5)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    programa = open_loop(tiempo,cadency, dutycycle, corriente_max_1,corriente_max_2 ,msi, pulse_width,t_subida, t_bajada,channels = (7,6))
    programa.start()
    print("iniciado")
    time.sleep(tiempo + 1)
    print("terminado")
    ch1,ch2=programa.stop()
    plt.title(f"Cadencia: {2*cadency}, tiempo programado: {tiempo}, tiempo real de ejecución {programa.tch2[-1]-programa.t0:.3}",fontsize = 12)
    plt.step(ch1[0],ch1[1],label="ch1",linewidth = 2)
    plt.step(ch2[0],ch2[1],label="ch2", linewidth = 2)
    plt.xlabel("tiempo [segundos]",fontsize = 10)
    plt.ylabel("corriente [mA]",fontsize = 10)
    plt.legend()
    plt.grid()
    plt.show()
