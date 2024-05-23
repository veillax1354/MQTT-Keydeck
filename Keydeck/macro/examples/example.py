import framework

def MyMacro():
    print("This is an example macro.")


macro = framework.Macro("MyMacro", "Example Macro", 1, "examples", MyMacro)
