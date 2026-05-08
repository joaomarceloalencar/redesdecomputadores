from socket import *

serverName = '200.129.39.124'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)


message = input('Forneça frase em letras minúsculas: ')
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print(modifiedMessage.decode())
clientSocket.close()
