import dht
from time import sleep
from machine import Pin, Timer, idle
from network import WLAN, STA_IF
from settings import WLAN_SSID, WLAN_PASSWORD

wlan = WLAN(STA_IF)
led = Pin(8, Pin.OUT)
pin = Pin(4)
d = dht.DHT11(pin)
timer = Timer(1)
temperature = 0

def wlan_connect():
    # activate wlan
    wlan.active(True)

    # connect to router
    wlan.connect(WLAN_SSID, WLAN_PASSWORD)

    # wait unitl wifi connects
    while not wlan.isconnected():
        idle()

    # blink leds
    for n in range(5):
        led.on()
        sleep(0.2)
        led.off()
        sleep(0.2)

def update(timer):
    global led, d, temperature

    led.toggle()
    d.measure()
    temperature = d.temperature()

# once per second
timer.init(freq=0.5, mode=Timer.PERIODIC, callback=update)

wlan_connect()

# print ip
ip = wlan.ipconfig('addr4')
print(ip[0])

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
                    font-size: 10rem;
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
