"""
Created on Monday Oct 30 23:38:00 2022

@author: Gerardo Ortíz Montúfar

"""

from controlStim import CntrlStim
from threading import Timer
from trapecio import getTrapecio
import time

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
candency = 30
dutycycle = .5
corriente_max = 10
msi = 20
pulse_width = 400
t_subida = 100
t_bajada = 100

#------------------------------------------------------------------------------
#INICIO PROGRAMA
#------------------------------------------------------------------------------

#Calculos de los tiempos
periodo_zancada = 60/30 #en segundos
apoyo = periodo_zancada*dutycycle
balanceo = periodo_zancada*(1-dutycycle)
t_meseta1 = apoyo*1e+3-(t_subida+t_bajada)
t_meseta2 = balanceo*1e+3-(t_subida+t_bajada)

#calculo del trapecio
t,vector1 = getTrapecio(t_subida,t_bajada,t_meseta1,msi,corriente_max)
t,vector2 = getTrapecio(t_subida,t_bajada,t_meseta2,msi,corriente_max)

vector1=[(pulse_width,c) for c in vector1] #se le pega el ancho de pulso en us
vector2=[(pulse_width,c) for c in vector2] 

#configuración del indicador


#inicializar la conexion con el estimulador y configuración
c_stim = CntrlStim(msi)

#rutina de watchdog si se requieren pausas
def rutina_wdg(pausa):
    t0 = time.time()
    while time.time()-t0 < pausa:
      c_stim.send_packet(c_stim.WATCHDOG)
      time.sleep(10e-3)


if __name__ == "__main__":
    try:
        while(True):
            c_stim.sendSignal(6,vector1) #canal 8
            c_stim.sendSignal(7,vector2) #canal 7
            #rutina_wdg()
            
    except KeyboardInterrupt:
        print("Protocolo de salida")
        c_stim.exitStim() 
