import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
REQUEST_FILE = "image.jpg"
MESSAGE = f"GET /{REQUEST_FILE}"
BUFFER_SIZE = 4000

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

with open("recebido_" + REQUEST_FILE, "wb") as f:
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        
        # Verifica o fim da transmissão
        if data == b"END":
            print("Arquivo recebido com sucesso.")
            break
        
        # Verifica mensagem de erro
        if data.startswith(b"ERROR"):
            print(data.decode())
            break

        # Obtém o número do pedaço e os dados
        chunk_info, file_data = data.split(b":", 1)
        f.write(file_data)  # Salva o pedaço no arquivo