# UDPServer.py
# Adaptado de Kurose & Ross, "Redes de Computadores e a Internet", Cap. 2.
# Servidor UDP que recebe uma mensagem, converte para maiusculas e devolve.

from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
