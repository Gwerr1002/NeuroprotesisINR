"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

"""

from resources.controlStim import CntrlStim
from resources.trapecio import getTrapecio
from resources.NP_GUI import QtCore
import time
from threading import Thread, Event
from playsound import playsound

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


class open_loop(QtCore.QObject):
    fin = QtCore.pyqtSignal(str)
    stimuli = QtCore.pyqtSignal(float,float,float)
    def __init__(self,tiempo, cadency, dutycycle, 
                max_current1,max_current2,
                msi, pw,
                t_ascent1, t_descent1,
                t_ascent2, t_descent2,
                channels = (6,7)):
        super().__init__()
        #canales del estimulador que se usaran
        self.channels = channels
        self.msi = msi
        #Calculos de los tiempos
        periodo_zancada = 60/cadency #en segundos
        apoyo = periodo_zancada*dutycycle
        balanceo = periodo_zancada*(1-dutycycle)
        t_meseta1 = apoyo*1e+3-(t_ascent1+t_descent1)
        t_meseta2 = balanceo*1e+3-(t_ascent2+t_descent2)
        #calculo del trapecio
        self.t1,self.v1 = getTrapecio(t_ascent1,t_descent1,t_meseta1,msi,max_current1)
        self.t2,self.v2 = getTrapecio(t_ascent2,t_descent2,t_meseta2,msi,max_current2)
        self.vector1=[(pw,msi,c,channels[0]) for c in self.v1] #se le pega el ancho de pulso en us
        self.vector2=[(pw,msi,c,channels[1]) for c in self.v2]
        #Numero de interaciones necesarias para cumplir con el tiempo dado
        self.N = int(round(tiempo/periodo_zancada))
        print(self.N)

        #Control de los graficos
        self.t0 = time.time() #inicio del programa

        #Ejecución del ciclo en un hilo distinto al del programa
        self.hilo = Thread(target=self.loop)
        self.end = Event()

        #inicializar la conexion con el estimulador y configuración
        playsound("resources/inicio.wav")
        self.c_stim = CntrlStim()

    def start(self):
        self.hilo.start()

    def stop(self):
        self.end.set()

    def loop(self):
        time.sleep(.5)
        self.t0 = time.time()
        for _ in range(self.N):
            Thread(target=playsound,args=("resources/sin440.wav",)).start()
            self.sendSignalQt(self.vector1)
            Thread(target=playsound,args=("resources/sin880.wav",)).start()
            self.sendSignalQt(self.vector2)
            if self.end.is_set():
                self.fin.emit("Abortado")
                self.c_stim.port.close()
                self.c_stim.exitStim()
                return
        self.c_stim.port.close()
        self.c_stim.exitStim()
        self.fin.emit("Finalizado\n")

    def sendSignalQt(self,vector):
        for pw,msi,c,canal in vector:
            #Enviar una corriente en el modo de pulso simple, el channel recibe un numero del 0 al 7
            self.c_stim.send_packet(self.c_stim.SINGLEPULSE, channel=canal, pulse_width=pw, current=c)
            self.stimuli.emit(time.time(),c,canal)
            time.sleep((msi-.8)*1e-3-pw*1e-6)

    def rutina_wdg(self):
        self.c_stim.send_packet(self.c_stim.WATCHDOG)

