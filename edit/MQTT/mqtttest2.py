import time
from MQTT.pahomqtt import MQTTClient as Paho
from machine import unique_id
import network

# bring up Wi‑Fi exactly as in your code…
# (copy _init_wifi logic here)

SSID = "tufts_eecs"
PASSWORD = "foundedin1883"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print(f"Connecting to Wi-Fi SSID={SSID}…", end="")
for _ in range(15):
    if wlan.status() >= 3:  # 3 means connected with IP
        print(" ok → IP=", wlan.ifconfig()[0])
        break
    print(".", end="")
    time.sleep(1)
else:
    raise RuntimeError("Wi-Fi connection failed")

# build the client
uid = ''.join('{:02x}'.format(b) for b in unique_id())
client = Paho(client_id="test_"+uid,
              server="10.247.137.92", port=1883)

# set up the callback
def cb(topic, msg):
    print("<<< CALLBACK >>>", topic, msg)

client.set_callback(cb)
client.connect()
print("Connected, now subscribing…")
client.subscribe("topic/test")

# loop
while True:
    client.check_msg()
    time.sleep_ms(100)
