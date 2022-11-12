# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control del estimulador. Hereda de la clase Stimulador, por lo que
posee los mismos métodos, parámetros y constantes de la clase padre. La llamada 
al constructor realizará la conexión con el estimulador. Cada uno de 
los metodos permitirá programar estimulaciones

"""

from concurrent.futures import thread
from pyRehastim import Stimulator
import serial.tools.list_ports as list_ports
import time
from threading import Timer

class CntrlStim(Stimulator):
    
    t_a = 50e-3 #tiempo de actualización en segundos
    
    def __init__(self, canales=0b11000000, p_msi = 20, pw=0x015E):
        '''
        Realiza la conexión con el estimulador, busca por el puerto de 
        conexión y procede a inicializar el estimulador.

        Parameters
        ----------
        p_msi : int
            Tiempo entre pulsos del estimulador en milisegundos. 
            El valor por defecto es 20 ms
        
        canales : binary
            Canales a activar. Se tienen 8 canales de los cuales, el LSB
            corresponde al canal 1 y el MSB al canal 8. Se coloca un uno
            en el canal que se desea activar. Por defecto se usan
            los canales 8 y 7 (0b11000000)

        Returns
        -------
        None.

        '''
        self.v_trapecio = [2,4,6,8,10,10,10,10,8,6,4,2]
        self.chanels = [{'mode':0,'pulse_width':pw,'current':0},{'mode':0,'pulse_width':pw,'current':0}]
        msi = 2*(p_msi - 1) #Se calcula el número que requiere el rehastim
        
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
            super().send_packet(super().INITCHANNELLISTMODE, lff=0, active_channels=canales,
            active_lf_channels=0x00, ipi=0, msi=msi, channel_execution=1)
            super().wait_for_packet(super().INITCHANNELLISTMODEACK)
            print("Conexion completada")
            #---------------------------------------------------------------------
            
        except AttributeError as a:
            print("Puerto no encontrado")
            print(a)
        
    def estimular(self,*args):
        print("actualizacion")
        canal = args[0]
        corriente = args[1]
        if canal == 1:
            self.chanels[1]['current'] = 0
        elif canal == 2:
            self.chanels[0]['current'] = 0
        else:
            print("No implementado")#levantar excepcion que no hay mas canales
        
        self.chanels[canal-1]['current'] = self.v_trapecio[corriente]
        # Envía configuración de canales (lista de diccionarios, un diccionario por canal)
        super().send_packet(super().STARTCHANNELLISTMODE, channel_config=self.chanels)
        #super().wait_for_packet(super().STARTCHANNELLISTMODEACK) #recibe datos del estimulador
        # Watchdog
        super().send_packet(super().WATCHDOG)
        #super().send_packet(super().WATCHDOG) #verificar de nuevo la necesidad de ejecutar dos veces

            
    def sendTrapecio(self, canal, vector):
        """
        

        Parameters
        ----------
        canal : TYPE
            DESCRIPTION.
        vector : TYPE, optional
            DESCRIPTION. The default is trapezoidal_prueba.

        Returns
        -------
        None.

        """
        self.timers = [Timer(CntrlStim.t_a*i,function = self.estimular,args = (canal,vector[i-1])) for i in range(1,len(vector)+1)]
        for timer in self.timers:
            timer.start()
        while self.timers[-1].is_alive():
            pass
        
    def exitStim(self):
        for timer in self.timers:
            if timer.is_alive():
                timer.cancel()
        super().send_packet(super().STOPCHANNELLISTMODE)
        super().__del__()



        

if __name__ == "__main__":
    from trapecio import getTrapecio

    t_subida = 150
    t_bajada = 100
    t_meseta = 200
    corriente_max = 10
    msi = 8
    pw = 100

    prueba = CntrlStim(p_msi = msi,pw=pw)
    #t,vector = getTrapecio(t_subida,t_bajada,t_meseta,corriente_max,msi,pw)
    t,vector = getTrapecio(t_subida,t_bajada,t_meseta,50,corriente_max)
    print(vector)

    try:
        while(True):
            prueba.sendTrapecio(1,vector)
            prueba.sendTrapecio(2,vector)
            
    except KeyboardInterrupt:
        print("Protocolo de salida")
        prueba.exitStim()
    
        