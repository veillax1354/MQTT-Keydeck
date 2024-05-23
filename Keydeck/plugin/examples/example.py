import framework

class Plugin:

    def __init__(self):
        super().__init__()

    def test(self):
        print("test")

    def test2(self, test2):
        print(test2)

plugin = framework.Plugin("MyPlugin", "Example Plugin", "Veillax", Plugin)
