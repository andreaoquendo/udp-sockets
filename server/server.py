import socket
import os
 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 4000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

def get_file(sock, addr, filename):
    if not os.path.isfile(filename):
        error_message = "ERROR: Arquivo não encontrado".encode()
        sock.sendto(error_message, addr)
        return

    print("found file")
    with open(filename, "rb") as f:
        chunk_number = 0
        while True:
            data = f.read(BUFFER_SIZE)  # Lê um pedaço do arquivo
            if not data:
                break  # Sai do loop quando não há mais dados
            
            # Anexa o número do pedaço ao início dos dados
            packet = f"{chunk_number}:".encode() + data
            sock.sendto(packet, addr)
            chunk_number += 1

        # Envia uma mensagem de fim de transmissão
        sock.sendto(b"END", addr)

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)

    request = data.decode()
    if request.startswith("GET"):
        print("GET REQUEST")
        _, filename = request.split(" ", 1)
        filename = filename.strip("/")
        get_file(sock, addr, filename)
    elif request.startswith("POST"):
        sock.sendto("post request".encode(), addr)
        _, filename = request.split(" ", 1)
        filename = filename.strip("/")
        # send_file(sock, addr, filename)
    else:
        error_message = "ERROR: Comando inválido".encode()
        sock.sendto(error_message, addr)