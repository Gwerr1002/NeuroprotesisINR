"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

"""

from RPI import RPI_cntrl
from controlStim import CntrlStim
from trapecio import getTrapecio
from time import sleep

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
t_subida = 100
t_meseta = 100
t_bajada = 100
pulse_width = 300
corriente_max = 10

#Protocolo de inicio
t,vector = getTrapecio(t_subida,t_bajada,t_meseta,msi,corriente_max)
vector = [(pulse_width,c) for c in vector]
c_rpi = RPI_cntrl()
c_stim = CntrlStim(msi)
flag = False #bandera que controla las interrupciones

c_stim.send_packet(c_stim.WATCHDOG)

"""
Protocolo de interrupción: aquí se configura lo que quieres que haga
la raspberry cuando detecte un cambio en los FSR.
"""
def interrupt_protocol(FSR):
    global flag
    global vector
    global ch1
    global ch2
    if not flag:
        flag = True
        if FSR == c_rpi.FSR_1:
            c_stim.sendSignal(ch1,vector)
        elif FSR == c_rpi.FSR_2:
            c_stim.sendSignal(ch1,vector)
        elif FSR == c_rpi.FSR_3:
            c_stim.sendSignal(ch2,vector)
        elif FSR == c_rpi.FSR_4:
            c_stim.sendSignal(ch2,vector)
        flag = False

c_stim.send_packet(c_stim.WATCHDOG)

#configuración y activación de las interrupciones
c_rpi.interrupciones(interrupt_protocol,t_subida+t_bajada+t_meseta)

#termina el protocolo de inicio

if __name__ == "__main__":
    try:
        while True:
            c_stim.send_packet(c_stim.WATCHDOG)
            sleep(.5)
    except KeyboardInterrupt:
        print("salida")
        c_rpi.GPIO_exit()
        c_stim.exitStim()