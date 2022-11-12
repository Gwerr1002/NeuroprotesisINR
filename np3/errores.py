# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 17:22:35 2022

@author: gerard
"""

class Disconected(Exception):
    def __init__(self):
        print("Estimulador desconectado aguarde para nueva conexion")
        
    def reconectar(self, arg):
        pass