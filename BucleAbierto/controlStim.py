# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control del estimulador. Hereda de la clase Stimulador, por lo que
posee los mismos métodos, parámetros y constantes de la clase padre. La llamada
al constructor realizará la conexión con el estimulador. Cada uno de
los metodos permitirá programar estimulaciones.

"""

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
        self.t_a = (msi-.8)*1e-3 #se le resta uno debido al restardo medido experimentalemte (veáse np5)
        try:
            print("Conectando con Rehastim")
            #Escanea el puerto en busca del ttyUSB0 (Puerto USB donde está conectado el rehastim)
            for p in list_ports.comports():
                if 'ttyUSB' in p[0]: #'ACM'
                    puerto_info = p

            #---------------------------------------------------------------------
            # Enlace y comunicacion con el rehastim
            #---------------------------------------------------------------------
            #Llamar al metodo __init__ de la clase Stimulator
            super().__init__(puerto_info[0])
            p_num = super().wait_for_packet(super().INIT)
            # y manda INITACK
            super().send_packet(super().INITACK, init_packet_number=p_num)
            print("Conexion completada")
            #---------------------------------------------------------------------

        except AttributeError as a:
            print("Puerto no encontrado")
            print(a)

    def sendSignal(self, canal, vector= trapezoidal_prueba):
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
            una tupla de la forma (pw,c), donde pw es el ancho de pulso y c es la
            corriente a estimualar. El valor por defecto es trapezoidal_prueba.

        Returns
        -------
        None.

        """
        for pw,msi,c in vector:
            #Enviar una corriente en el modo de pulso simple, el channel recibe un numero del 0 al 7
            super().send_packet(super().SINGLEPULSE, channel=canal, pulse_width=pw, current=c)
            time.sleep(self.t_a-pw*1e-6)

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
    msi = 10

    t,vector = getTrapecio(t_subida,t_bajada,t_meseta,msi,corriente_max)
    print(vector)
    vector=[(300,c) for c in vector] #se le pega el ancho de pulso en us
    prueba = CntrlStim(msi)
    try:
        while(True):
            prueba.sendSignal(6,vector) #canal 8
            prueba.sendSignal(7,vector) #canal 7

    except KeyboardInterrupt:
        print("Protocolo de salida")
        prueba.exitStim()
