import keyboard as kb
import requests
import win32api
import webbrowser
import subprocess
from pynput.keyboard import Key, Controller
import json
import os
from typing import Any
import importlib

keyboard = Controller()
Key = Key

class PluginException(Exception):
    pass
    
class MacroException(Exception):
    pass
    

class Macro:

    def __init__(self, name: str, desc: str, id: int, folder: str, set_run=None):
        self.name = name
        self.desc = desc
        self.id = id
        self.folder = folder
        if set_run is not None:
            self.run = set_run
        else:
            self.run = self.default_run

    def default_run(self):
        """Default run method that does nothing."""
        print(__name__ + " - This is a macro example. This is being printed due to no function passed to the constructor as 'set_run'.")

    def run(self):
        """Execute the custom run function if provided, otherwise use the default."""
        if hasattr(self, 'run'):
            self.run()
        else:
            self.default_run()


class Plugin:

    def __init__(self, name: str, description: str, author: str, set_class):
        """
        Custom Plugins
        :param name: Plugin Name
        :type name: str
        :param description: Plugin Description
        :type description: str
        :param author: Plugin Author
        :type author: str
        :param set_class: Class containing the functionality for the plugin
        :type set_class: Any
        """
        self.name = name
        self.description = description
        self.author = author
        self.__set_class = set_class
        setattr(self, f"{self.name}", self.__set_class)

    def register(self):
        try:
            with open(os.path.join(os.getcwd(), "plugins.json"), "r+") as f:
                plugins = json.load(f)
                f.seek(0)
                plugins[self.name] = {
                    "author": self.author,
                    "description": self.description,
                    "args": self.args
                }
                f.truncate()
                json.dump(plugins, f)
                f.flush()
            print(f"Successfully loaded plugin {self.name} from {self.author}")
        except FileNotFoundError:
            print(f"Failed to find plugins.json. Please create one.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            
            
plugins = {}

def scan_plugins():
    print("Scanning for plugins")
    directory_path = os.path.join(os.getcwd(), "plugin")
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
                plugin_instance = getattr(module, 'plugin', None)  # Get the Macro instance from the module
                if plugin_instance is not None:
                    plugins[plugin_instance.name] = plugin_instance
    print("Finished scanning for plugins - " + str(len(plugins)) + " found, " + str(len(plugins)) + " loaded.")          
    
    
def get_plugin(name: str):
    print(f"Searching for {name} in {plugins}")
    try:
        return plugins[name]
    except:
        print(f"Plugin {name} not found")
        raise PluginException("Plugin not found")


if __name__ == '__main__':

    def custom_run(macro_instance):
        print(f"Custom run for {macro_instance.name} executed.")

    macro_example = Macro('Example Macro', 'This is just an example.', 1, 'example_folder')

    # Running the macro with the custom run function
    macro_example.run()

    class custom:

        def __init__(self):
            super().__init__()

        def test(self):
            print("test")

        def test2(self):
            print("test2")

    plugin = Plugin("Plugin", "example", "veillax", custom)

    c = plugin.Plugin()
    c.test()
    c.test2()
