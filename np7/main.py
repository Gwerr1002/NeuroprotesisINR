import bluetooth
from bucle_abierto import open_loop
from bucle_cerrado import closed_loop

#funciones

def call_op_loop():
    op_loop=open_loop(30,.5,10,20,300,100,100)
    op_loop.start()
    return op_loop

def call_clsd_loop():
    clsd_loop = closed_loop(100,100,200,10,20,300,1,1,1,1)
    clsd_loop.start()
    return clsd_loop

#constantes

COMMANDS = {
    b'1': call_op_loop,
    b'2': call_clsd_loop,
    b'3': "stop"
}

host = ""
port = 1

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM) #tipo de comunicación

try:
    server.bind((host,port))
    print("Completado")
except Exception:
    print("No completado")

server.listen(1)
print("Conectado")
cliente, direccion = server.accept()
print("cliente:",cliente,"\ndireccion: ",direccion)
try:
    while True:
        datos = cliente.recv(1024) #datos recibidos, 1024 es el tamaño del buffer
        COMMAND = COMMANDS[datos]
        print("Comando recibido")
        if COMMAND == "stop":
            COMMAND.stop()
        else:
            COMMAND()
        cliente.send(datos)
except KeyboardInterrupt:
    print("salida")
    server.close()
    cliente.close()