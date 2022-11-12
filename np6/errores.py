# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 17:22:35 2022

@author: gerard
"""

class InvalidChannel(Exception):
    def __init__(self):
        print("""Canal inválido, seleccione un canal en un rango de 0 a 7 donde
        0 corresponde al canal 1 y 7 al canal 8""")