VERSION = "0.0.2.0"
FRAMEWORK_VERSION = "0.0.1.0"

import argparse

import os
import threading
import time
import json
import importlib
import framework

import dotenv
import paho.mqtt.client as mqtt
from PIL import Image
from pystray import Icon, Menu, MenuItem

dotenv.load_dotenv()

q: bool = False

HOST: str = os.getenv("HOST")
PORT: int = 1883
MQTT_USERNAME: str = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD")
KEEPALIVE: int = 60

macros_dict = {}


def scan_macros():
    print("Scanning for macros")
    directory_path = os.path.join(os.getcwd(), "macro")
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith('.py'):  # Check if the file is a Python file
                spec = importlib.util.spec_from_file_location(
                    os.path.splitext(filename)[0],
                    os.path.join(root, filename)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # Execute the module

                # Assuming each macro script defines a 'main' function and creates a Macro instance
                macro_instance = getattr(module, 'macro', None)  # Get the Macro instance from the module
                if macro_instance is not None:
                    macros_dict[(macro_instance.id, macro_instance.folder)] = macro_instance
    print("Finished scanning for macros - " + str(len(macros_dict)) + " found, " + str(len(macros_dict)) + " loaded.")                


def run_macro(macros_dict, id, folder):
    """
    Runs a macro by its ID and folder.
    :param macros_dict: Dictionary of macros organized by (id, folder).
    :param id: The ID of the macro to run.
    :param folder: The folder of the macro to run.
    :return: None
    """
    try:
        if (id, folder) in macros_dict:
            print(f"Running macro with ID {id} and folder {folder}")
            macros_dict[(id, folder)].run()
        else:
            print(f"No macro found with ID {id} and folder {folder}")
    except Exception as e:
        print(f"Failed to execute macro {folder}/{id}: {e}")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("Subscribing to topic")
    client.subscribe("/macro/#")


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(msg.topic + " - " + str(payload))
    run_macro(macros_dict, payload["macro_id"], payload["folder"])


def connect():
    # Connect to the broker
    client.connect(HOST, PORT, KEEPALIVE)


def on_disconnect(client, userdata, rc):
    global q
    if not q:
        print("Disconnected unexpectedly. Attempting to reconnect.")
        client.reconnect_delay_set(1, 60)  # Set initial delay to 10 seconds, max to 60 seconds


# Create an Icon object
icon = Icon("KeyDeck", Image.open("img.png"), "MQTT Macro Pad")

# Create a client instance
client = mqtt.Client(client_id="mqtt-key-deck", protocol=mqtt.MQTTv311)

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Set authentication credentials
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)


def close():
    global q
    icon.stop()
    q = True


def mqtt_restart():
    client.disconnect()
    connect()


# Create a Menu object
menu = Menu(MenuItem("Scan for new macros", scan_macros), MenuItem("Scan for new plugins", framework.scan_plugins), MenuItem("Restart MQTT", mqtt_restart), MenuItem("Quit", close))

icon.menu = menu


def main():
    framework.scan_plugins()
    scan_macros()
    
    connect()

    # Start the loop in the background so that the program can continue doing other things
    client.loop_start()

    try:
        while True:
            if q:
                raise KeyboardInterrupt
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        client.disconnect()
        client.loop_stop()

        close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='store_true',
                        help='Display program version')

    args = parser.parse_args()

    if args.version:
        print("Running Keydeck software v" + VERSION)
        print("Running Keydeck Framework v" + FRAMEWORK_VERSION)
    else:
        threading.Thread(target=main).start()
        icon.run()
