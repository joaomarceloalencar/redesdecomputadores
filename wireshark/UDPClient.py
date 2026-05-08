# UDPClient.py
# Adaptado de Kurose & Ross, "Redes de Computadores e a Internet", Cap. 2.
# Cliente UDP que envia uma frase e recebe-a de volta em maiusculas.
#
# Antes de executar, ajuste serverName para o IP ou hostname do servidor.

from socket import *

serverName = 'ALTERAR_PARA_IP_DO_SERVIDOR'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input('Input lowercase sentence: ')
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()
