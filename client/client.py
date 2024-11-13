import socket
import zlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
REQUEST_FILE = "image.jpg"
MESSAGE = f"Hello"
BUFFER_SIZE = 8000

def retransmit_message(filename, chunk_number):
    

if __name__ == "__main__":

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = -1
    while addr == -1:
        addr = input("Insert server ip:port: ")
        try:
            ip, port = addr.split(":")
            sock.sendto(MESSAGE.encode(), (ip, int(port)))
            print(f"Message sent to {UDP_IP}:{UDP_PORT}")
            
            sock.settimeout(2)
            try:
                response, server = sock.recvfrom(BUFFER_SIZE)
                print(f"Server responding normally")
            except socket.timeout:
                print("No response received; the server may not be reachable or is not responding.")
            
        except Exception as error:
            print(f"Error connecting to server: {error}")
            addr = -1

    while True: 
        message = input("Insert command [GET /<file> -m <recieved file name>| RETRANSMIT <chunk number> \<file> ]:\n")
        command, file_name = message.split(" -m ")
        sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
        recieved_chunks = []
        while True:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            
            if data == b"END":
                print("End of transmission.")
                break
            
            if data.startswith(b"ERROR"):
                print(data.decode())
                break

            recieved_chunks.append(data)         
        
        print("Verifying file...")
        drop_chunk = input(f"recieved {len(recieved_chunks)}, drop chunk? (number ex: 1,4,5/not)")
        delete_chunks = []
        if drop_chunk != "n":
            delete_chunks = drop_chunk.split(",")
            delete_chunks = [int(x.strip()) for x in delete_chunks]
        else: 
            print("yes?")
        print(delete_chunks)

        chunks_dict = {}
        for chunk in recieved_chunks:
            chunk_number, checksum, file_data = chunk.split(b":", 2)
            received_checksum = int(checksum.decode())
            calculated_checksum = zlib.crc32(file_data)
            if received_checksum != calculated_checksum:
                reply = input(f"Error: Incorrect checksum on {chunk_number.decode()}. Retransmit?")

                if reply != "y":
                        print("Aborting...")
                
                _, filename = command.split(" ", 1)
                retransmit_command = f"RETRANSMIT {chunk_number} {file_name}"
                sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
                while True:
                    data, _ = sock.recvfrom(BUFFER_SIZE)
                    
                    if data == b"END":
                        print("End of transmission.")
                        break
                    
                    if data.startswith(b"ERROR"):
                        print(data.decode())
                        break

                    recieved_chunks.append(data) 
                  
            chunks_dict[int(chunk_number)] = file_data

        print(chunks_dict.keys())
        for i in delete_chunks:
            chunks_dict.pop(i)
        print(chunks_dict.keys())

        max_size = max(chunks_dict) + 1
        for i in range(0, max_size):
            if i not in chunks_dict.keys():
                reply = input(f"Chunk number {i} lost. Retransmit? (y/n) ")
                if reply != "y":
                    print("Aborting...")
                
                _, filename = command.split(" ", 1)
                retransmit_command = f"RETRANSMIT {i} {filename}"
                sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
                while True:
                    data, _ = sock.recvfrom(BUFFER_SIZE)
                    
                    if data == b"END":
                        print("End of transmission.")
                        break
                    
                    if data.startswith(b"ERROR"):
                        print(data.decode())
                        break

                    recieved_chunks.append(data)
                    chunks_dict[i] = data  


        with open("recebido_" + file_name, "wb") as f:   
            for i in sorted(chunks_dict.keys()):
                f.write(chunks_dict[i])
            f.close()
                
