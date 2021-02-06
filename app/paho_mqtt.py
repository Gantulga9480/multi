import paho.mqtt.client as mqtt
from datetime import datetime as dt
import csv


class PahoMqtt:

    def __init__(self, broker, info, port=1883,
                 raw_msg=False, c_msg="", d_msg=""):
        self.__broker = broker
        self.__port = port
        self.info = info
        self._c_msg = c_msg
        self._d_msg = d_msg
        self.__client = mqtt.Client(f"{info} control")
        if not raw_msg:
            self.__client.on_message = self.__on_message
        else:
            self.__client.on_message = self.__on_message_raw
        self.__client.on_connect = self.__on_connect
        self.__client.on_publish = self.__on_publish
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.wait_for_publish = self.__wait_for_publish
        self.__client.connect(self.__broker, self.__port)
        self.is_streaming = False
        self.is_started = False
        self.sensor_ready = False
        self.label = None
        self.counter = 0
        self.counter_temp = 0
        self.death_counter = 0

    def stream_init(self, path):
        self._file = open(f'{path}/sensor_{self.info}.csv', "w+", newline='')
        self._writer = csv.writer(self._file)
        self.is_streaming = True
        self.is_started = True

    def stream_stop(self):
        self.is_streaming = False

    def __on_connect(self, client, userdata, level, buf):
        print(f"{self._c_msg} connected")

    def __on_message(self, client, userdata, message):
        self.counter += 1
        if self.counter > 10000:
            self.counter = 0
        self.sensor_ready = True
        if self.is_streaming:
            msg = message.payload.decode("utf-8", "ignore")
            msg = msg.replace("[", "")
            msg = msg.replace("]", "")
            msg = msg.replace(" ", "")
            if self.label:
                self._writer.writerow([dt.now(), msg, self.label])
                self.label = None
            else:
                self._writer.writerow([dt.now(), msg, 0])

    def __on_message_raw(self, client, userdata, message):
        pass

    def __on_publish(self, client, userdata, result):
        print('command published')

    def __on_disconnect(self, client, userdata, rc):
        self.sensor_ready = False
        print(f"{self._d_msg} disconnected")

    def __wait_for_publish(self):
        print('waiting to publish command')

    def disconnect(self):
        self.__client.disconnect()

    def publish(self, topic, msg, qos=0):
        self.__client.publish(topic, payload=msg, qos=qos)

    def subscribe(self, topic, qos=0):
        self.__client.subscribe(topic, qos=qos)

    def loop_start(self):
        self.__client.loop_start()
