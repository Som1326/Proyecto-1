from UI2 import Application2
from algorithms import ModEx

if __name__ == "__main__":
    modex = ModEx()
    app = Application2(modex)
    app.run()