# mqtt.py
import time
import network
import machine
from machine import unique_id
from MQTT.pahomqtt import MQTTClient as Paho

CONFIG_FILE = "config.txt"

LED = machine.Pin('LED', machine.Pin.OUT)

class MQTTClient:
    def __init__(
        self,
        cmd_topic="topic/xrpinvitational",
        tag_topic="topic/xrpinvitational",
        config_file=CONFIG_FILE
    ):
        # topics
        self.cmd_topic = cmd_topic
        self.tag_topic = tag_topic

        # load wifi + config
        self._load_config(config_file)

        # bring up Wi‑Fi
        if not self._init_wifi(self.ssid, self.wifi_pass):
            raise RuntimeError("Wi-Fi connection failed")

        # small pause for link to settle
        time.sleep_ms(200)

        # build unique client ID
        uid = "".join("{:02x}".format(b) for b in unique_id())
        client_id = f"{self.client_base_id}_{uid}"

        # create & connect socket
        self.client = Paho(
            client_id=client_id,
            server=self.mqtt_server,
            port=self.mqtt_port,
            user=self.mqtt_user or None,
            password=self.mqtt_password or None,
            keepalive=self.mqtt_keepalive,
            ssl=self.mqtt_ssl
        )
        self.client.set_callback(self._dispatch)
        self.client.connect()
        print(f"MQTT: Connected to {self.mqtt_server}:{self.mqtt_port} as {client_id}")

        # subscribe once—no thread
        self.client.subscribe(self.cmd_topic)
        print(f"Subscribed to '{self.cmd_topic}'")

        # placeholder for user callback
        self._cmd_handler = None

    def _load_config(self, filename):
        # defaults
        self.ssid          = "Tufts_Robot"
        self.wifi_pass     = ""
        self.mqtt_server   = "10.247.137.92"
        self.mqtt_port     = 1883
        self.mqtt_user     = None
        self.mqtt_password = None
        self.mqtt_keepalive= 60
        self.mqtt_ssl      = False
        self.client_base_id= "XRP-Client"

        try:
            with open(filename) as f:
                for line in f:
                    if not line.strip() or line.startswith("#"):
                        continue
                    key, val = line.strip().split("=", 1)
                    setattr(self, key.lower(), val)
        except OSError:
            print(f"Config file '{filename}' not found; using defaults.")

    def _init_wifi(self, ssid, password, timeout=10):
        print(f"Connecting to Wi‑Fi SSID='{ssid}'…", end="")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        
        LED.on()  # Turn on the LED to indicate Wi-Fi connection attempt

        for _ in range(timeout):
            if wlan.status() >= 3:
                ip = wlan.ifconfig()[0]
                print(f" ok, IP={ip}")
                return True
            time.sleep(1)
            print(".", end="")
        print("\nWi‑Fi connection timeout.")
        return False

    def set_command_callback(self, handler):
        """Register your Robot.handle_command(topic, msg)."""
        self._cmd_handler = handler

    def _dispatch(self, topic, msg):
        print(f"[MQTT] dispatching {topic} , {msg}")
        topic_s = topic.decode() if isinstance(topic, bytes) else topic
        print(f"[MQTT Rx] {topic_s} , {msg}")
        if topic_s == self.cmd_topic and self._cmd_handler:
            self._cmd_handler(topic_s, msg)
        else:
            print(f"[MQTT] unhandled topic: {topic_s}")

    def publish(self, topic, msg):
        self.client.publish(topic, msg)

    def check_msg(self):
        #print("here")
        """Call this in your main loop to process incoming packets."""
        self.client.check_msg()