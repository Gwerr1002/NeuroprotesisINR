"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

"""
from RPI import RPI_cntrl
from controlStim import CntrlStim
from trapecio import getTrapecio
from time import sleep, time
from threading import Thread, Event
from numpy import append, array
import matplotlib.pyplot as plt
from playsound import playsound

"""
Configuración de los canales de estimulación, se pueden usar 
numeros de 0 al 7. Donde el canal 1 corresponde al 0 y el canal
8 al al 7
"""
ch1 = 6
ch2 = 7

"""
Parámetros de estimulación:
    + msi : Main Stimulation Interval, debe indicarse en millisegundos, el mínimo es de 8.
            Por motivos de la aplicación se debe cuidar que no supere el tiempo de WATCHDOG
            que es de 1200 ms
    + t_subida: El tiempo de subida que requiere el trapecio en millisegundos
    + t_bajada: Tiempo de bajada del trapecio en millisegundos
    + t_meseta: Tiempo de meseta del trapecio en millisegundos
    + pulse_width: Ancho de pulso en microsegundos [0,500 us]
"""
msi = 10
t_subida = 300
t_meseta = 300
t_bajada = 300
pulse_width = 350
corriente_max = 10

class closed_loop():
    cntrl=Event()
    alive=False
    FSR_12 = False #variable que indica si el sensor 1 o 2 fue presionado
    FSR_34 = True #variable que indica si el sensor 3 o 4 fue presionado, se inicializa como True por motivos de la aplicacion

    def __init__(self,t_ascent,t_descent,t_top,max_current,msi,pw,V1REF,V2REF,V3REF,V4REF,channels = (6,7)):
        self.channels = channels
        self.msi = msi
        self.t, self.v = getTrapecio(t_ascent,t_descent,t_top,msi,max_current)
        self.v_reg = self.v
        self.v = [(pw,c) for c in self.v]
        self.c_rpi = RPI_cntrl(V1REF,V2REF,V3REF,V4REF)
        #control del bucle
        closed_loop.cntrl.set()
        #Control del registro de datos (guardar secuencia de estimulación desde el inicio del programa)
        self.t0 = time() #inicio del programa
        self.tch1 = [] #guarda tiempos de estimulación del canal ch1
        self.tch2 = []
        #configuración y activación de las interrupciones
        self.c_rpi.interrupciones(self.call_interrupt,self.stop,int(self.t[-1]))
        self.c_stim = CntrlStim(msi)
    
    def interrupt_protocol(self,FSR):
        closed_loop.cntrl.clear()
        if (FSR == self.c_rpi.FSR[0] or FSR == self.c_rpi.FSR[1]) and closed_loop.FSR_34:
            closed_loop.FSR_34 = False
            self.tch1.append(time())
            #Thread(target=playsound,args=("sin.wav",)).start()
            self.c_stim.sendSignal(self.channels[0],self.v)
            closed_loop.FSR_12 = True
        elif (FSR == self.c_rpi.FSR[2] or  FSR == self.c_rpi.FSR[3]) and closed_loop.FSR_12:
            closed_loop.FSR_12 = False
            self.tch2.append(time())
            self.c_stim.sendSignal(self.channels[1],self.v)
            closed_loop.FSR_34 = True
        closed_loop.cntrl.set()

    def call_interrupt(self,FSR):
        Thread(target=self.interrupt_protocol,args=(FSR,)).start()

    def start(self):
        closed_loop.alive=True
        Thread(target=self.loop()).start()

    def stop(self,btn):
        closed_loop.alive = False
        self.c_stim.exitStim()
        self.c_rpi.GPIO_exit()
    
    def loop(self):
        while closed_loop.alive:
            if closed_loop.cntrl.is_set():
                self.c_stim.send_packet(self.c_stim.WATCHDOG)
                sleep(.5)
            else:
                closed_loop.cntrl.wait()

    def get_channels(self):
        t = append(0,self.t)
        t = append(t,self.t[-1]+self.msi)
        v = append(append(0,self.v_reg),0)
        tch1_reg = [(i-self.t0) for i in self.tch1]
        tch2_reg = [(i-self.t0) for i in self.tch2]
        tch1 = array([0])
        c1 = tch1
        tch2 = array([0])
        c2 = tch2
        for i in tch1_reg:
            tch1 = append(tch1,t/1000+i)
            c1 = append(c1,v)
        for i in tch2_reg:
            tch2 = append(tch2,t/1000+i)
            c2 = append(c2,v)

        return (tch1,c1),(tch2,c2)
    
    def plot_chs(self):
        ch1,ch2=self.get_channels()
        plt.title("Estimulación")
        plt.step(ch1[0],ch1[1],label="ch1")
        plt.step(ch2[0],ch2[1],label="ch2")
        plt.xlabel("tiempo [segundos]")
        plt.ylabel("corriente [mA]")
        plt.legend()
        plt.grid()
        plt.show()


if __name__ == "__main__":
    prog = closed_loop(t_subida,t_bajada,t_meseta,corriente_max,msi,pulse_width,1,1,1,1,(ch1,ch2))
    prog.start()
    while closed_loop.alive:
        pass
    prog.plot_chs()
