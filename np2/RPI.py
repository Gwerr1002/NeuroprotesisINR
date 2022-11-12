# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 22:57:50 2022

@author: Gerardo Ortíz Montúfar

Clase para el control de la Raspberry Pi 4
"""

import RPi.GPIO as GPIO
import time

class RPI_cntrl():
	def __init__(self,f=1000,dc1=20,dc2=20,dc3=20,dc4=20):
		#Para los FSR del talón se asignan los pines GPIO
		self.FSR_1 = 29
		self.FSR_2 = 31
		#los últimos dos para el antepíe
		self.FSR_3 = 33
		self.FSR_4 = 35
		#Asignación de pines dedicados a PWM
		self.pwm_1 = 11
		self.pwm_2 = 12
		self.pwm_3 = 13 #cuidado con el 14, es tierra
		self.pwm_4 = 15
		self.pwm_5 = 16 #destinado al beep
		self.confGPIO(f,dc1,dc2,dc3,dc4)

	def confGPIO(self,f,dc1,dc2,dc3,dc4):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		#Se configuran los pines correspondientes a sensores como entradas
		GPIO.setup(self.FSR_1, GPIO.IN)
		GPIO.setup(self.FSR_2, GPIO.IN)
		GPIO.setup(self.FSR_3, GPIO.IN)
		GPIO.setup(self.FSR_4, GPIO.IN)
		#Se configuran los pines destinados a PWM como salidas
		GPIO.setup(self.pwm_1, GPIO.OUT)
		GPIO.setup(self.pwm_2, GPIO.OUT)
		GPIO.setup(self.pwm_3, GPIO.OUT)
		GPIO.setup(self.pwm_4, GPIO.OUT)
		GPIO.setup(self.pwm_5, GPIO.OUT)
		#Instancias de la clase PWM
		self.PWM_1 = GPIO.PWM(self.pwm_1, f)
		self.PWM_2 = GPIO.PWM(self.pwm_2, f)
		self.PWM_3 = GPIO.PWM(self.pwm_3, f)
		self.PWM_4 = GPIO.PWM(self.pwm_4, f)
		self.PWM_5 = GPIO.PWM(self.pwm_5, 1136) #nota La
		self.PWM_1.start(dc1)
		self.PWM_2.start(dc2)
		self.PWM_3.start(dc3)
		self.PWM_4.start(dc4)

	def beep(self):
		self.PWM_5.ChangeFrequency(1136)
		self.PWM_5.start(50)
		time.sleep(.5)
		self.PWM_5.stop()


	def interrupciones(self,accion):
		self.IN1 = GPIO.add_event_detect(self.FSR_1,GPIO.RISING,accion,200) #modificar o borrar debounce, tal vez ajustar al tiempo de ejecucion del trapecio
		#self.IN2 = GPIO.add_event_detect(self.FSR_2,GPIO.RISING,accion) #modificar o borrar debounce
		self.IN3 = GPIO.add_event_detect(self.FSR_3,GPIO.RISING,accion,200)
		#self.IN4 = GPIO.add_event_detect(self.FSR_4,GPIO.RISING,accion)

	def GPIO_exit(self):
		self.PWM_1.stop()
		self.PWM_2.stop()
		self.PWM_3.stop()
		self.PWM_4.stop()
		self.PWM_5.stop()
		GPIO.cleanup()


if __name__ == "__main__":
	print("Hola")
	a = RPI_cntrl()
	def msj(canal):
		if canal == a.FSR_1:
			print("Se presiono FSR1")
		elif canal == a.FSR_3:
			print("Se presiono FSR3")
		else:
			print("No implementado")
	a.interrupciones(msj)
	try:
		while(1):
			a.beep()
			time.sleep(.5)
	except KeyboardInterrupt:
		a.GPIO_exit()