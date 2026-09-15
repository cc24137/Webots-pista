import struct
import socket
import _thread

from controller import Robot, Camera, Display

status_sentido = False

# dados para criar um servidor socjet para receber mensagens
def get_porta():
    return 9001

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP

def on_new_client(socket, addr):
    global status_sentido
    while True:
        msg = socket.recv(1024)
        if msg:
            print('olha a mensagem')
            break
        else:
            break
    req = msg.decode()
    if req.__contains__('anda'):
        status_sentido = True
    print(req)
    socket.close()
    return

# define o servidor
def servidor(https, hport):
    sockHttp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockHttp.bind((https, hport))
    except:
        sockHttp.bind(('', hport))
    
    sockHttp.listen(1)
    print(f'Iniciou o servidor em {get_ip()} na porta {get_porta()}')
    while True:
        client, addr = sockHttp.accept()
        _thread.start_new_thread(on_new_client, (client, addr))
        
# inicializa a thread do socket servidor
_thread.start_new_thread(servidor, (get_ip(), get_porta()))


# programacao de movimento e sensores

robot = Robot()

timestep = int(robot.getBasicTimeStep())

print("iniciando rodas")

motorE = robot.getDevice('motorE')
motorE.setPosition(float('inf'))
motorE.setVelocity(0.0)

motorE2 = robot.getDevice('motorE2')
motorE2.setPosition(float('inf'))
motorE2.setVelocity(0.0)


motorD = robot.getDevice('motorD')
motorD.setPosition(float('inf'))
motorD.setVelocity(0.0)

motorD2 = robot.getDevice('motorD2')
motorD2.setPosition(float('inf'))
motorD2.setVelocity(0.0)

ds = robot.getDevice('DS')
dse = robot.getDevice('DSE')
dsd = robot.getDevice('DSD')

ds.enable(timestep)
dse.enable(timestep)
dsd.enable(timestep)


camera = robot.getDevice('camera')
refresh_rate_ms = 64
camera.enable(refresh_rate_ms)
display = robot.getDevice('display')

sentido = False
vini_e = 0
vini_d = 0



VEL_MAX = 1.0

while robot.step(timestep) != -1:    
    ve = round(dse.getValue(), 2)
    vd = round(dsd.getValue(), 2)
    
    e_preto = ve >= 5 
    d_preto = vd >= 5 
    
    # 1. ARMADILHA DE CÍRCULO / CRUZAMENTO (Ambos no preto)
    if e_preto and d_preto:
        # Quando os dois sensores pegam preto (cruzamento ou rotatória)
        # Gira para um lado para escapar e seguir apenas uma das bordas
        motorE.setVelocity(VEL_MAX)
        motorE2.setVelocity(VEL_MAX)
        motorD.setVelocity(-VEL_MAX * 0.5)
        motorD2.setVelocity(-VEL_MAX * 0.5)

    # 2. CURVA ACENTUADA PARA A ESQUERDA
    elif e_preto and not d_preto:
        # Roda esquerda gira para TRÁS com força total, direita para FRENTE
        # Isso faz uma curva extremamente fechada (gira no próprio eixo)
        motorE.setVelocity(-VEL_MAX)
        motorE2.setVelocity(-VEL_MAX)
        motorD.setVelocity(VEL_MAX)
        motorD2.setVelocity(VEL_MAX)
                
    # 3. CURVA ACENTUADA PARA A DIREITA
    elif d_preto and not e_preto:
        # Roda direita gira para TRÁS com força total, esquerda para FRENTE
        motorE.setVelocity(VEL_MAX)
        motorE2.setVelocity(VEL_MAX)
        motorD.setVelocity(-VEL_MAX)
        motorD2.setVelocity(-VEL_MAX)
        
    # 4. LINHA RETA (Ambos no branco) - O fim da dança!
    else: 
        # Se a linha está no meio (nenhum sensor toca nela), apenas vá reto!
        motorE.setVelocity(VEL_MAX)
        motorE2.setVelocity(VEL_MAX)
        motorD.setVelocity(VEL_MAX)
        motorD2.setVelocity(VEL_MAX)

    # Processamento da câmera
    image = camera.getImage()
    if display and image:
        img_ref = display.imageNew(image, Display.BGRA, camera.getWidth(), camera.getHeight())
        display.imagePaste(img_ref, 0, 0, False)
        display.imageDelete(img_ref)
    