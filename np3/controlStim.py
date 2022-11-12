# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control del estimulador. Hereda de la clase Stimulador, por lo que
posee los mismos métodos, parámetros y constantes de la clase padre. La llamada 
al constructor realizará la conexión con el estimulador. Cada uno de 
los metodos permitirá programar estimulaciones

"""

from pyRehastim import Stimulator
import serial.tools.list_ports as list_ports
import time

class CntrlStim(Stimulator):
    
    trapezoidal_prueba = [(200,1),(200,2),(200,3),(200,4),(200,5),(200,6),(200,7),
                          (200,8),(200,9),(200,9),(200,9),(200,9),(200,8),(200,7),
                          (200,6),(200,5),(200,4),(200,3),(200,2),(200,1)]
    
    def __init__(self, msi):
        '''
        Realiza la conexión con el estimulador, busca por el puerto de 
        conexión y procede a inicializar el estimulador.

        Parameters
        ----------
        p_msi : int
            Tiempo entre pulsos del estimulador en milisegundos. 
            El valor por defecto es 20 ms
        
        canales : binary
            Canales a activar. Se tienen 8 canales de los cuales, el bit 0
            corresponde al canal 1 y el bit 7 al canal 8. Se coloca un uno
            en el canal que se desea activar. Por defecto se usan
            los canales 8 y 7 (0b11000000)

        Returns
        -------
        None.

        '''
        #self.t_a = msi*1e-3-100e-6 #tiempo de actualización en segundos 100us corrsponde a la pausa entre las dos fases del pulso
        self.t_a = 20e-3
        try:
            print("Conectando con Rehastim")
            #Escanea el puerto en busca del ttyUSB0 (Puerto USB donde está conectado el rehastim)
            for i,p in enumerate(list_ports.comports()):
                if 'ttyUSB' in p[0]:
                    puerto_info = p
            
            #---------------------------------------------------------------------
            # Enlace y comunicacion con el rehastim
            #---------------------------------------------------------------------
            #Llamar al metodo __init__ de la clase Stimulator
            super().__init__(puerto_info[0])
            p_num = super().wait_for_packet(super().INIT)
            # y manda INITACK
            super().send_packet(super().INITACK, init_packet_number=p_num) #pnum marcado como 0x00
            print("Conexion completada")
            #---------------------------------------------------------------------
            
        except AttributeError as a:
            print("Puerto no encontrado")
            print(a)
            
    def sendTrapecio(self, canal, vector= trapezoidal_prueba):
        """
        

        Parameters
        ----------
        canal : binary
            Indique el canal a usar en binario, considerando que el bit 0 es para el canal 1 
            y el bit 7 para el canal 8.
        vector : 
            DESCRIPTION. The default is trapezoidal_prueba.

        Returns
        -------
        None.

        """
        for pw,c in vector:
            super().send_packet(super().SINGLEPULSE, channel=canal, pulse_width=pw, current=c)
            time.sleep(self.t_a-pw*1e-6)
        
    def exitStim(self):
        super().send_packet(super().STOPCHANNELLISTMODE)
        super().__del__()        

if __name__ == "__main__":
    from trapecio import getTrapecio

    t_subida = 300#100
    t_bajada = 300#100
    t_meseta = 400#100
    corriente_max = 10
    msi = 20

    t,vector = getTrapecio(t_subida,t_bajada,t_meseta,msi,corriente_max)
    print(vector)
    vector=[(300,c) for c in vector] #se le pega el ancho de pulso en us
    prueba = CntrlStim(msi)
    try:
        while(True):
            prueba.sendTrapecio(6,vector) #canal 8
            prueba.sendTrapecio(7,vector) #canal 7
            
    except KeyboardInterrupt:
        print("Protocolo de salida")
        prueba.exitStim()
    
        