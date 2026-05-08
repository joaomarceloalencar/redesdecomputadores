from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("O servidor está pronto para receber.")

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print ("Mensagem recebida de {}: {}".format(clientAddress, message.decode()))
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)

