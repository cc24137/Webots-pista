import socket

# dados para criar um servidor socket para receber mensagens

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP
   
def enviar_mensagem(mensagem, ip=None, port=None):
    ip = ip or get_ip()
    port = port or get_porta()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(mensagem.encode())
        print(f'mensagem enviada: {mensagem}')
    except ConnectionRefusedError:
        print('não foi possivel conectar')
    finally:
        sock.close()
        

if __name__ == '__main__':
    msg = input("digite o comando : ")
    enviar_mensagem(msg)    
    