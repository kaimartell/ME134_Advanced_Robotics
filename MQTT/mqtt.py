import time
import json
import _thread
import network
from machine import unique_id
from pahomqtt import MQTTClient

CONFIG_FILE = "config.txt"

class MQTTClient:
    def __init__(self,
                 cmd_topic="robot/commands",
                 tag_topic="robot/tag",
                 config_file=CONFIG_FILE):
        #topics
        self.cmd_topic = cmd_topic
        self.tag_topic = tag_topic

        #load wifi
        self._load_config(config_file)

        # Bring up Wi-Fi
        if not self._init_wifi(self.ssid, self.wifi_pass):
            raise RuntimeError("Wi-Fi connection failed")

        # Build unique client ID
        uid = ''.join('{:02x}'.format(b) for b in unique_id())
        client_id = f"{self.client_base_id}_{uid}"

        # Connect to MQTT broker
        self.client = MQTTClient(client_id=client_id,
                                 server=self.mqtt_server,
                                 port=self.mqtt_port,
                                 user=self.mqtt_user or None,
                                 password=self.mqtt_password or None,
                                 keepalive=self.mqtt_keepalive,
                                 ssl=self.mqtt_ssl,
                                 ssl_params=self.mqtt_ssl_params)
        self.client.connect()
        print(f"MQTT: Connected to {self.mqtt_server}:{self.mqtt_port} as {client_id}")

        # Setup callback dispatch
        self._cmd_handler = None
        self.client.set_callback(self._dispatch)

    def _load_config(self, filename):
        # Set defaults
        self.ssid = CONFIG_FILE.get('ssid', None)
        self.wifi_pass = CONFIG_FILE.get('password', None)
        self.mqtt_server = CONFIG_FILE.get('mqtt_server', None)
        self.mqtt_port = 1883
        self.mqtt_user = None
        self.mqtt_password = None
        self.mqtt_keepalive = 60
        self.mqtt_ssl = False
        self.mqtt_ssl_params = {}
        self.client_base_id = "XRP-Client"

        try:
            with open(filename) as f:
                for line in f:
                    if not line.strip() or line.startswith('#'):
                        continue
                    key, val = line.strip().split('=',1)
                    setattr(self, key.lower(), val)
        except OSError:
            print(f"Config file '{filename}' not found; using defaults.")

    def _init_wifi(self, ssid, password, timeout=10):
        print(f"Connecting to Wi-Fi SSID='{ssid}'...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

        for _ in range(timeout):
            if wlan.status() >= 3:
                print("Wi-Fi connected; IP=" + wlan.ifconfig()[0])
                return True
            time.sleep(1)
            print('.', end='')
        print("\nWi-Fi connection timeout.")
        return False

    def set_command_callback(self, handler):
        self._cmd_handler = handler

    def _dispatch(self, topic, msg):
        topic_s = topic.decode() if isinstance(topic, bytes) else topic
        if topic_s == self.cmd_topic and self._cmd_handler:
            self._cmd_handler(topic_s, msg)
        else:
            print(f"MQTT unhandled: {topic_s} -> {msg}")

    def subscribe_commands(self, qos=0):
        self.client.subscribe(self.cmd_topic, qos)
        print(f"Subscribed to '{self.cmd_topic}'")
        
    def publish(self, msg):
        self.client.publish(self.topic, msg)

    def start(self, on_thread=True, delay_ms=100):
        if on_thread:
            _thread.start_new_thread(self._loop, (delay_ms,))
            print("MQTT loop running in background thread.")
        else:
            self._loop(delay_ms)

    def _loop(self, delay_ms):
        try:
            while True:
                self.client.check_msg()
                time.sleep_ms(delay_ms)
        except KeyboardInterrupt:
            print("MQTT loop stopped by user.")
