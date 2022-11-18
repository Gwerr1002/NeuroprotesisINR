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
    + corriente_max: corriente máxima del trapecio en milliamperes
    + msi : Main Stimulation Interval, debe indicarse en millisegundos, el mínimo es de 8ms.
            Por motivos de la aplicación se debe cuidar que no supere el tiempo de WATCHDOG
            que es de 1200 ms
    + pulse_width: Ancho de pulso en microsegundos [0,500 us]
    + t_subida: El tiempo de subida que requiere el trapecio en millisegundos
    + t_bajada: Tiempo de bajada del trapecio en millisegundos
"""

cadency = 30
dutycycle = .5
corriente_max = 10
msi = 20
pulse_width = 400
t_subida = 100
t_bajada = 100

class open_loop():
    
    def __init__(self, cadency, dutycycle, max_current,msi, pw,t_ascent, t_descent,channels = (6,7)):

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
        self.t1,self.v1 = getTrapecio(t_ascent,t_descent,t_meseta1,msi,max_current)
        self.t2,self.v2 = getTrapecio(t_ascent,t_descent,t_meseta2,msi,max_current)
        self.vector1=[(pw,c) for c in self.v1] #se le pega el ancho de pulso en us
        self.vector2=[(pw,c) for c in self.v2]

        #Control del registro de datos (guardar secuencia de estimulación desde el inicio del programa)
        self.t0 = time.time() #inicio del programa
        self.tch1 = [] #guarda tiempos de estimulación del canal ch1
        self.tch2 = []

        #Ejecución del ciclo en un hilo distinto al del programa
        self.hilo = Thread(target=self.loop)
        self.end = Event()

        #inicializar la conexion con el estimulador y configuración
        self.c_stim = CntrlStim(msi)

    def start(self):
        open_loop.is_alive = True
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
        while not self.end.is_set():
            Thread(target=playsound,args=("sin.wav",)).start()
            self.tch1.append(time.time())
            self.c_stim.sendSignal(self.channels[0],self.vector1)
            self.tch2.append(time.time())
            self.c_stim.sendSignal(self.channels[1],self.vector2)
        self.c_stim.port.close()
        self.c_stim.exitStim()

    def rutina_wdg(self):
        self.c_stim.send_packet(self.c_stim.WATCHDOG)
        time.sleep(0.5)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    programa = open_loop(cadency, dutycycle, corriente_max,msi, pulse_width,t_subida, t_bajada,channels = (7,6))
    programa.start()
    time.sleep(1800)
    ch1,ch2=programa.stop()
    plt.title("Estimulación")
    plt.step(ch1[0],ch1[1],label="ch1")
    plt.step(ch2[0],ch2[1],label="ch2")
    plt.xlabel("tiempo [segundos]")
    plt.ylabel("corriente [mA]")
    plt.legend()
    plt.grid()
    plt.show()