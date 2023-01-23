class Menu:
    def __init__(self):
        print("Iniciando programa...")
        self.debug_commands = {
            "turn_on_oven": "Ligar forno",
            "turn_off_oven": "Desligar forno",
            "turn_on_heating": "Ligar aquecimento",
            "turn_off_heating": "Desligar aquecimento",
            "change_mode": "Alterar modo de operação",
            "update_constants": "Atualizar parâmetros Kp, Ki e Kd",
            "update_reference_temperature": "Atualizar temperatura de referência",
        }

    def select_mode(self) -> int:
        print("=====================================")
        print("Selecione o modo de operação do forno")
        print("1 - Modo Dasbord")
        print("2 - Modo Curva")
        print("3 - Modo Terminal (debug)")
        print("4 - Sair")
        print("=====================================")
        #  make sure the user enters a valid option
        while True:
            try:
                option = int(input("Digite o número da opção: "))
                if option in range(1, 5):
                    break
                raise ValueError
            except ValueError:
                print("Digite um número válido")
                continue
        return option

    def select_debug_command(self):
        # self.clear_screen()
        print("Para sair da aplicação, pressione Ctrl+C")
        print("Ao ligar o forno e o aquecimento, o programa entrará em loop")
        print("e não será possível sair até que o forno atinja a temperatura")
        print("de referência")
        print("=====================================")
        print("Selecione o modo de operação do forno")
        # print commands with numbers
        for i, command in enumerate(self.debug_commands):
            print(f"{i + 1} - {self.debug_commands[command]}")
        print("=====================================")
        #  make sure the user enters a valid option
        while True:
            try:
                option = int(input("Digite o número da opção: "))
                if option in range(1, len(self.debug_commands) + 2):
                    break
            except ValueError:
                print("Digite um número válido")
                continue
        # format the option to the command
        if option == 6:
            return "back"
        return list(self.debug_commands.keys())[option - 1]

    def ask_for_reference_temperature(self) -> float:
        while True:
            try:
                reference_temperature = float(
                    input("Informe a temperatura de referência(TR):")
                )
                break
            except ValueError:
                print("Digite um número válido")
                continue
        return reference_temperature

    def ask_for_constants(self):
        # ask if the user wants to update the constants
        while True:
            try:
                option = int(
                    input(
                        "Deseja atualizar os parâmetros? \nValores padrões Kp=30.0, Ki=0.2, Kd=400.0\n(1 - Sim, 2 - Não): "  # noqa: E501
                    )
                )
                if option in range(1, 3):
                    break
                raise ValueError
            except ValueError:
                print("Digite um número válido")
                continue
        # if the user doesn't want to update the constants, return the default values
        # Kp=30.0,
        # Ki=0.2,
        # Kd=400.0,
        if option == 2:
            return 30.0, 0.2, 400.0

        while True:
            try:
                kp = float(input("Informe o valor de Kp: "))
                ki = float(input("Informe o valor de Ki: "))
                kd = float(input("Informe o valor de Kd: "))
                break
            except ValueError:
                print("Digite um número válido")
                continue
        return kp, ki, kd

    def clear_screen(self):
        print("\033c", end="")
        print("\x1bc", end="")
        print("\x1b[2J", end="")
