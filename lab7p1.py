# webserver_threaded.py
#
# Serve the web page in a separate thread

import socket
import RPi.GPIO as GPIO
import threading
from time import sleep

GPIO.setmode(GPIO.BCM)

pins = (2,3,4)
freq = 60
ledbrs = [1,2,3]
for p in pins: GPIO.setup(p, GPIO.OUT)
for i in range(len(pins)): ledbrs[i] = GPIO.PWM(pins[i], freq)

def change_brightness(led, br):
        led.ChangeDutyCycle(br)


# Helper function to extract key,value pairs of POST data
def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n')+4
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

# Generate HTML for the web page:
def web_page():
    #rows = [f'<tr><td>{str(p)}</td><td>{GPIO.input(p)}</td></tr>' for p in pins]
    html = """
        <html>
        <body>


        <form action="POST">
          <label for="brightness">Brightness:</label><br>
          <input type="range" id="brightness" name="brightness" value=0><br>
          <label for="led">LED:</label><br>
          <input type="radio" id="LED 1" name="led" value="1">
          <label for="LED 1">LED 1</label><br>
          <input type="radio" id="LED 2" name="led" value="2">
          <label for="LED 2">LED 2</label><br>
          <input type="radio" id="LED 3" name="led" value="3">
          <label for="LED 3">LED 3</label><br><br>
          <input type="submit" value="Change Brightness">
        </form> 

        </body>
        </html>
        """
    #print(html)
    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object

# Serve the web page to a client on connection:
def serve_web_page():
    try:
        while True:
            print('Waiting for connection...')
            conn, (client_ip, client_port) = s.accept()     # blocking call
            print(f'Connection from {client_ip} on client port {client_port}')
            client_message = conn.recv(2048).decode('utf-8')
            print(f'Message from client:\n{client_message}')
            data_dict = parsePOSTdata(client_message)
            print(data_dict)
            if 'led' in data_dict.keys():
                modledindex = ledbrs[data_dict["led"]-1]
            else:
                modledindex = 0
            if 'brightness' in data_dict.keys():
                br = data_dict["brightness"]
            else:
                br = 0
            print(modledindex,br)
            #change_brightness(modledindex,br)
            conn.send(b'HTTP/1.1 200 OK\r\n')                  # status line
            conn.send(b'Content-Type: text/html\r\n')          # headers
            conn.send(b'Connection: close\r\n\r\n')   
            try:
                conn.sendall(web_page())                       # body
            finally:
                conn.close()

        
    except:
        print('Closing socket')
        s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # pass IP addr & socket type
s.bind(('', 80))     # bind to given port
s.listen(3)          # up to 3 queued connections

webpageThread = threading.Thread(target=serve_web_page)
webpageThread.daemon = True
webpageThread.start()


# Do whatever we want while the web server runs in
# a separate thread:
try:
    while True:
        pass

except:
    print('Joining webpageThread')
    webpageThread.join()
    print('Closing socket')
    s.close()
    #for pwm in ledbrs: pwm.stop()
    GPIO.cleanup()
