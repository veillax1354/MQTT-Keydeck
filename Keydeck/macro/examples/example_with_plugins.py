import framework

pl = framework.get_plugin("MyPlugin")
plugin = pl.MyPlugin()

def macro():
    plugin.test()
    plugin.test2("test2-arg")

macro = framework.Macro(name="Plugin Example", desc="An example of how to use a plugin", id=101, folder="examples", set_run=macro)
