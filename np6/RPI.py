# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control de la Raspberry Pi 4
"""

import RPi.GPIO as GPIO
import time

class RPI_cntrl():
	def __init__(self,v1=.5,v2=.5,v3=.5,v4=.5):
		'''
        Realiza la configuración correspondiente de la Raspberry Pi 4B entorno a los pines GPIO,
		configura entradas y salidas y protocolo de interrupciones.

        Parameters
        ----------
        v1 : float, optional
            Voltaje de referencia del DAC OUTA, el valor por defecto es .5 volts
		
		v2 : float, optional
            Voltaje de referencia del DAC OUTB, el valor por defecto es .5 volts

		v3 : float, optional
            Voltaje de referencia del DAC OUTC, el valor por defecto es .5 volts
		
		v4 : float, optional
            Voltaje de referencia del DAC OUTD, el valor por defecto es .5 volts

        Returns
        -------
        None.

        '''
		#Para los FSR del talón se asignan los pines 29 y 31 los últimos dos son para el antepíe
		self.FSR = [29,31,33,35]
		#Asignación de pines dedicados al DAC
		self.DAC = [11,13,15,16] #INA,INB,INC,IND
		self.BTN = 18 #Botón de paciente para terminar la secuencia
		self.confGPIO()
		self.updateVolt(v1,v2,v3,v4)

	def confGPIO(self):
		"""
        Metodo encargado de configurar los pines GPIO de la RaspberryPi en el modo
		BOARD (numeración de pines)

        Parameters
        ----------
        None. 

        Returns
        -------
        None.

        """

		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		#Se configuran los pines correspondientes a sensores como entradas
		for FSR in self.FSR:
			GPIO.setup(FSR, GPIO.IN)
		#Se configuran los pines destinados el control del DAC como salidas
		for D in self.DAC:
			GPIO.setup(D, GPIO.OUT)
		#Configuración del botón de paciente para salir de la secuencia
		GPIO.setup(self.BTN,GPIO.IN)
	
	def updateVolt(self,*args):
		"""
		Configura las salidas del DAC OUTA,OUTB,OUTC en el modo sample/hold
		bajo la fórmula dada en el datasheet:
		VO = TPWH*VREF/TPER
		+ VO : es el voltaje de la salidas del DAC
		+ TPHW : es el ancho de pulso.
		+ TPER : es el periodo
		+ VREF : es el voltaje de referencia interno del DAC (2.5 volts)

		Parameters
        ----------
        args : tuple
			Prámetros correspondientes a las cuatro salidas del DAC VOUTA, VOUTB,
			VOUTC y VOUTD, deseados.

        Returns
        -------
        None.
		"""
		TPER = 20e-3 #Es el periodo más estable
		VREF = 2.5 #voltaje de referecnia interno del DAC
		if len(args) > 4:
			print("Solo puedes configurar 4 voltajes de referencia en el DAC")
			raise Exception
		for i in range(4):
			TPHW = args[0]*TPER/VREF
			for j in range(10):
				GPIO.output(self.DAC[i],GPIO.HIGH)
				time.sleep(TPHW)
				GPIO.output(self.DAC[i],GPIO.LOW)
				time.sleep(TPER-TPHW)
			GPIO.output(self.DAC[i],GPIO.HIGH)

	def interrupciones(self,accion,stop,debounce = 200):
		"""
		Genera los objetos que activan las interrupciones del GPIO y se le asigna a
		cada uno un protocolo de interrupción

		Parameters
        ----------
        accion : function
				Es el protocolo de interrupciones, es decir, lo que quieres que haga
				cuando se detecte una interrupcion, este debe recibir el número de pin
				en dónde se detecta la interrupción. Tiene el objetivo de aplicar
				la estimulación cuando se detecte un cambio.

		stop : function
				Es el protocolo de interrupción para apagar el programa en caso de que
				se presione el botón de paciente. Tiene un debounce de 200 ms fijo.

		debounce : int, optional
				Es el tiempo, en millisegundos, en el cual se ignora cualquier interrupcion 
				que pudiera generarse por un cambio en los pines con deteccion de eventos tras 
				una interrupcion detectada. La librería RPi.GPIO lo añade como una opción para
				evitar los rebotes que pudieran generarse. El valor por defecto es 200 ms
		
        Returns
        -------
        None.
		"""
		flanco = [GPIO.RISING,GPIO.RISING,GPIO.FALLING,GPIO.FALLING] #flanco de detección
		for i in range(4):#configuración de interrupciones de los FSR
			GPIO.add_event_detect(self.FSR[i],flanco[i],accion,debounce)
		GPIO.add_event_detect(self.BTN,GPIO.RISING,stop,200) #configuración de interrupción del boton de paciente

	def GPIO_exit(self):
		"""
		Metodo de salida en donde solo se limpian las configuraciones
		realizadas.

		Parameters
        ----------
        None

        Returns
        -------
        None.
		"""
		GPIO.cleanup()

#Las siguientes lineas son para probar la clase

if __name__ == "__main__":
	import time
	print("Hola")
	a = RPI_cntrl()
	def msj(canal):
		if canal == a.FSR[0]:
			print("Se presiono FSR1")
		elif canal == a.FSR[2]:
			print("Se presiono FSR3")
		else:
			print("No implementado")
	a.interrupciones(msj)
	try:
		while True:
			time.sleep(.5)
	except KeyboardInterrupt:
		a.GPIO_exit()