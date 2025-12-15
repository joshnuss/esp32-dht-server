import dht
from time import sleep
from machine import Pin, Timer

import machine
from network import WLAN, STA_IF
from settings import WLAN_SSID, WLAN_PASSWORD

print(WLAN_SSID)
print(WLAN_PASSWORD)

# station interface
wlan = WLAN(STA_IF)

# activate wlan
wlan.active(True)

# connect to router
wlan.connect(WLAN_SSID, WLAN_PASSWORD)

# wait for wifi to connect
while not wlan.isconnected():
    machine.idle() 

# get ip
ip = wlan.ipconfig('addr4')
print(ip[0])

led = Pin(8, Pin.OUT)
pin = Pin(4)
d = dht.DHT11(pin)
timer = Timer(1)
temperature = 20

def tick(timer):
    global led, d, temperature

    led.toggle()
    d.measure()
    temperature = d.temperature()

# once per second
timer.init(freq=0.5, mode=Timer.PERIODIC, callback=tick)

from microdot import Microdot, Response

app = Microdot()

Response.default_content_type = 'text/html'

@app.route('/')
async def index(request):
    return f"""
    <html>
        <head>
            <link rel="preconnect" href="https://rsms.me/">
            <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
            <title>Temperature</title>
            <style>
                body {{
                    color: #444;
                    display: grid;
                    place-items: center;
                    font-size: 4rem;
                    font-family: Inter, sans;
                }}

                h1 {{
                    display: flex;
                }}

                h1 sup {{
                    color: #666;
                    font-size: 40%;
                }}
            </style>
        </head>
        <body>
            <h1>{temperature}<sup>°C</sup></h1>
        </body>
    </html>
    """

@app.route('/api')
async def json(request):
    return {"temperature": temperature}

app.run(debug=True, port=80)
