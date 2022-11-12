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
msi = 50
t_subida = 300
t_meseta = 300
t_bajada = 300
pulse_width = 350
corriente_max = 10

#------------------------------------------------------------------------------
#INICIO DE PROGRAMA
#------------------------------------------------------------------------------

#Protocolo de inicio
t,vector = getTrapecio(t_subida,t_bajada,t_meseta,msi,corriente_max)
vector = [(pulse_width,c) for c in vector]
c_rpi = RPI_cntrl(1,1,1,1)
c_stim = CntrlStim(msi)
flag = False #bandera que controla las interrupciones
FSR_12 = False #variable que indica si el sensor 1 o 2 fue presionado
FSR_34 = True #variable que indica si el sensor 3 o 4 fue presionado, se inicializa como True por motivos de la aplicacion

c_stim.send_packet(c_stim.WATCHDOG)

def interrupt_protocol(FSR):
    """
    Protocolo de interrupción: aquí se configura lo que quieres que haga
    la raspberry cuando detecte un cambio en los FSR.

    Prameters
    ---------

    FSR : int 
        Es el número de PIN en donde se detecto la interrupción, el usuario no debe
        de indicarlo ya que la función se pasa como decorador al target de la 
        interrupción

    Returns
    -------

    None
    """
    global flag,vector,ch1,ch2,FSR_12,FSR_34
    
    if not flag:
        flag = True
        print("Detectado {}".format(FSR))
        if (FSR == c_rpi.FSR[0] or FSR == c_rpi.FSR[1]) and FSR_34:
            FSR_34 = False
            c_stim.sendSignal(ch1,vector)
            FSR_12 = True
        elif (FSR == c_rpi.FSR[2] or  FSR == c_rpi.FSR[3]) and FSR_12:
            FSR_12 = False
            c_stim.sendSignal(ch2,vector)
            FSR_34 = True
        flag = False


#configuración y activación de las interrupciones
c_rpi.interrupciones(interrupt_protocol,500)

#termina el protocolo de inicio

if __name__ == "__main__":
    try:
        while True:
            if not flag:
                c_stim.send_packet(c_stim.WATCHDOG)
            sleep(.5)
    except KeyboardInterrupt:
        print("salida")
        c_rpi.GPIO_exit()
        c_stim.exitStim()