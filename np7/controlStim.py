# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control del estimulador. Hereda de la clase Stimulador, por lo que
posee los mismos métodos, parámetros y constantes de la clase padre. La llamada
al constructor realizará la conexión con el estimulador. Se puede usar
el método para enviar el WATCHDOG de la calse padre y el método de esta clase
sendSignal para generar cualquier secuencia de estimulación deseada.
después de la línea if __name__ == "__main__": Se puede ver un ejemplo de uso
de esta clase con una secuencia de estimulaciones modulada trapezoidalmente
"""

import platform
from pyRehastim import Stimulator
import serial.tools.list_ports as list_ports
import time

class CntrlStim(Stimulator):

    def __init__(self):
        '''
        Realiza la conexión con el estimulador, busca por el puerto de
        conexión y procede a inicializar el estimulador.

        Parameters
        ----------
        p_msi : int, optional
            Main Stimulation Interval (MSI), tiempo entre pulsos del estimulador en milisegundos.
            El valor por defecto es 20 ms, el inverso es el Main Stimulation Frequency (MSF).

        Returns
        -------
        None.

        '''
        try:
            print("Conectando con Rehastim")
            #Verificar sistema operativo (los nombres de los puertos se llaman de forma distinta)
            if platform.system() == 'Windows':
                port_name = 'COM'
            elif platform.system() == 'Linux':
                port_name = 'ttyUSB'#ttyUSB
            #Escanea el puerto en busca del ttyUSB0 (Puerto USB donde está conectado el rehastim)
            for p in list_ports.comports():
                if port_name in p[0]:
                    puerto_info = p

            #---------------------------------------------------------------------
            # Enlace y comunicacion con el rehastim
            #---------------------------------------------------------------------
            #Llamar al metodo __init__ de la clase Stimulator
            super().__init__(puerto_info[0])
            #p_num = super().wait_for_packet(super().INIT)
            # y manda INITACK
            #super().send_packet(super().INITACK, init_packet_number=p_num)
            print("Conexion completada")
            #---------------------------------------------------------------------

        except AttributeError as a:
            print("Puerto no encontrado")
            print(a)

    def sendSignal(self, canal, vector):
        """
        Envía una secuencia de corrientes contenidas en una lista. Con una frecuencia
        1/MSI, con el modo single pulse.

        Parameters
        ----------
        canal : int
            Indique el canal a usar como un entero del 0 al 7, en el cual el cero
            corresponde al canal 1 y el 7 al canal 8
        vector : list, optional
            Es la secuencia de estimulación, cada entrada de la lista debe contener
            una tupla de la forma (pw,msi,c), donde pw es el ancho de pulso, c es la
            msi es el main stimulation interval
            corriente a estimular. El valor por defecto es trapezoidal_prueba.

        Returns
        -------
        None.

        """
        for pw,msi,c in vector:
            #Enviar una corriente en el modo de pulso simple, el channel recibe un numero del 0 al 7
            super().send_packet(super().SINGLEPULSE, channel=canal, pulse_width=pw, current=c)
            time.sleep((msi-.8)*1e-3-pw*1e-6)

    def exitStim(self):
        """
        Rutina de salida, cierra el puerto serial
        """
        super().__del__()

#El siguiente código es una prueba de la clase

if __name__ == "__main__":
    from trapecio import getTrapecio

    t_subida = 100
    t_bajada = 100
    t_meseta = 100
    corriente_max = 10
    pulse_width = 300
    msi = 10

    t,vector = getTrapecio(t_subida,t_bajada,t_meseta,msi,corriente_max)
    print(vector)
    vector=[(pulse_width,msi,c) for c in vector] #se le pega el ancho de pulso en us
    prueba = CntrlStim()
    try:
        while(True):
            prueba.sendSignal(6,vector) #canal 8
            prueba.sendSignal(7,vector) #canal 7

    except KeyboardInterrupt:
        print("Protocolo de salida")
        prueba.exitStim()
