from launcher import Inicializador

def main():
    if not Inicializador().iniciar():
        return
    from interface import InterfaceAutomacao

    interface = InterfaceAutomacao()
    interface.iniciar()

if __name__ == "__main__":
    main()
