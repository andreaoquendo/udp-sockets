import socket
import os
import zlib
 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 7800

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

def get_file(sock, addr, filename):
    if not os.path.isfile(filename):
        error_message = "ERROR: File not found".encode()
        sock.sendto(error_message, addr)
        return

    with open(filename, "rb") as f:
        chunk_number = 0
        while True:
            data = f.read(BUFFER_SIZE) 
            if not data:
                break  
            checksum = zlib.crc32(data)
            
            packet = f"{chunk_number}:{checksum}:".encode() + data
            sock.sendto(packet, addr)
            chunk_number += 1

        sock.sendto(b"END", addr)

def retransmit_file(sock, addr, filename, chunk):
    if not os.path.isfile(filename):
        error_message = "ERROR: File not found".encode()
        sock.sendto(error_message, addr)
        return

    file_dict = {}
    with open(filename, "rb") as f:
        chunk_number = 0
        while True:
            data = f.read(BUFFER_SIZE) 
            if not data:
                break  
            file_dict[chunk_number] = data
            chunk_number += 1

    try:
        data = file_dict[chunk]
        checksum = zlib.crc32(data)
        packet = f"{chunk_number}:{checksum}:".encode() + data
        sock.sendto(packet, addr)
        sock.sendto(b"END", addr)
    except Exception as e:
        error_message = "ERROR: {e}"
        sock.sendto(error_message, addr)
        return

if __name__ == "__main__":
    port = -1
    while port == -1: 
        port = input("Insert server port: ")
        try: 
            port = int(port)
            sock.bind((UDP_IP, port))
            print(f"Server running on {UDP_IP}:{port}")
        except Exception as e:
            print(e)
            print(f"Invalid port {port}")
            port = -1

    while True:
        data, addr = sock.recvfrom(2048) 

        request = data.decode()
        if request.startswith("GET"):
            _, filename = request.split(" ", 1)
            filename = filename.strip("/")
            get_file(sock, addr, filename)
        elif request.startswith("RETRANSMIT"):
            _, chunk, filename = request.split(" ", 2)
            filename = filename.strip("/")
            retransmit_file(sock, addr, filename, int(chunk))
        else:
            error_message = "ERROR: Comando inválido".encode()
            sock.sendto(error_message, addr)