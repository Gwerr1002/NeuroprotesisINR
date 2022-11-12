import bluetooth

host = ""
port = 1

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM) #tipo de comunicación

try:
    server.bind((host,port))
    print("Completado")
except Exception:
    print("No completado")

server.listen(1)
cliente, direccion = server.accept()
print("cliente:",cliente,"\ndireccion: ",direccion)
try:
    while True:
        datos = cliente.recv(1024) #datos recibidos, 1024 es el tamaño del buffer
        print(datos)
        cliente.send(datos)
except KeyboardInterrupt:
    print("salida")
    server.close()
    cliente.close()