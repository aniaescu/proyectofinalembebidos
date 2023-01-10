import RPi.GPIO as GPIO
import time,sys
import smbus

bus = smbus.SMBus(1)

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

# Establecemos los pines a usar, y los definimos como entrada o salida
# segun el sensor

GPIO_PULSADOR = 17 # Defino el número del PIN del pulsador

GPIO_ZUMBADOR = 26 # Defino el número del PIN del zumbador

GPIO.setup(GPIO_PULSADOR, GPIO.IN) # Defino el PIN del pulsador como entrada

GPIO.setup(GPIO_ZUMBADOR, GPIO.OUT) # Defino el PIN del zumbador como salida

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e
DISPLAY_LUMI_ADDR = 0x29


# Funcion para modificar los color del LCD RGB (los valores que se inserten tienen que estar entre 0..255)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# Funciones para escribir en la LCD
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
    


# Utilizamos esta función para realizar un sonido, que será más contínuo o más intermitete
# dependiendo del valor de la variable distancia.
def sonido(estado):
    if estado == 'verde':
        inicio = time.time()
        final = time.time() + 1
        while inicio <= final:
            #print('verde')
            GPIO.output(GPIO_ZUMBADOR, False)
            inicio = time.time()
        GPIO.output(GPIO_ZUMBADOR, True)
    elif estado == 'rojo':
        GPIO.output(GPIO_ZUMBADOR, True)
    else:
        GPIO.output(GPIO_ZUMBADOR, False)
    
    
def color(color):
    luz = luminosidad()
    try:
        if color == "r":
            if luz < 100:
                setRGB(255,0,0)
            else: 
                setRGB(30,0,0)
            sonido('rojo')

        elif color == "a":
            if luz < 100:
                setRGB(255,128,0)
            else:
                setRGB(60,30,0)
            sonido('naranja')
        elif color == "v":
            if luz < 100:
                setRGB(0,255,0)
            else:
                setRGB(0,30,0)
            sonido('verde')
        elif color == "n":
            setRGB(0,0,0)

    except KeyboardInterrupt:
        setText("KeyboardInterrupt")
        setRGB(255,0,0)
    except IOError:
        setText("IOError")
        setRGB(255,0,0)

#Funcion a la que llamamos para inciar el programa
def semaforo():
    while True:
        verde()

#Funcion para cuando el semaforo este en verde.
def verde():
    # Verde
    inicio = time.time()
    final = time.time() + 12
    while inicio <= final:
        color('v')
        inicio = time.time()
        dif = int(final - inicio)
        if dif >= 0:
            setText(str(dif))
        time.sleep(0.1)
    naranja()

#Funcion para cuando el semaforo este en naranja.
def naranja():
    # Naranja
    inicio = time.time()
    final = time.time() + 5
    setText('Se va a poner en rojo!')
    while inicio <= final:
        color('a')
        time.sleep(0.5)
        color('n')
        inicio = time.time()
        time.sleep(0.5)
    rojo()

#Funcion para cuando el semaforo este en rojo
def rojo():
    # Rojo
    inicio = time.time()
    final = time.time() + 21
    while inicio <= final:
        if GPIO.input(GPIO_PULSADOR) == GPIO.HIGH:
            print(int(final - inicio))
            color('r')
            inicio = time.time()
            print('SIN PULSAR')
            dif = int(final - inicio)
            setText(str(dif))
            time.sleep(0.1)
        elif int(final - inicio) >= 15:
            print(int(final - inicio))
            color('r')
            inicio = time.time()
            print('PULSAR 5 SEGUNDOS')
            dif = int(final - inicio)
            setText(str(dif))
            time.sleep(0.1)
        elif int(final - inicio) < 15:
            semaforo()
            print('PULSAR')

        


#Funcion para calcular la luminosidad que hay.
def luminosidad():
    bus.write_byte_data(DISPLAY_LUMI_ADDR, 0x00 | 0x80, 0x03)
    data0 = bus.read_i2c_block_data(DISPLAY_LUMI_ADDR, 0x0C | 0x80, 2)
    data1 = bus.read_i2c_block_data(DISPLAY_LUMI_ADDR, 0x0E | 0x80, 2)
    ch0 = data0[1] * 256 + data0[0] 
    ch1 = data1[1] * 256 + data1[0] 
    return ch0-ch1

if __name__=="__main__":
    semaforo()

