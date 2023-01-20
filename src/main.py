from oven import Oven
from time import sleep

if __name__ == "__main__":
    print("Iniciando programa")
    # Create a menu to select the mode
    print("=====================================")
    print("Selecione o modo de operação do forno")
    print("1 - Modo fixo")
    print("2 - Modo curva")
    print("3 - Modo Debug")
    print("=====================================")
    mode = input("Digite o número do modo: ")
    oven = Oven()
    if mode == "1":
        oven.intialize()
        try:
            commands = {
                "turn_on_oven": oven.turn_on,
                "turn_off_oven": oven.turn_off,
                "turn_on_heating": oven.start_heating,
                "turn_off_heating": oven.stop_heating,
                "change_mode": oven.change_mode,
            }
            loop = 0
            while True:
                user_command = oven.read_user_command()
                print(f"User command: {user_command}")
                commands.get(user_command, oven.empty)()
                loop += 1
                sleep(0.5)
                if loop == 2:
                    oven.control_temperature()
                    loop = 0
        except KeyboardInterrupt:
            oven.down()
    elif mode == "2":
        oven.turn_on_mode_curve()
        oven.intialize()
    elif mode == "3":
        print("Modo debug")
        reference_temperature = float(
            input("Informe a temperatura de referência(TR):")
        )
        print("Deseja atualizar os parâmetros Kp, Ki e Kd?")
        response = input("Digite 's' para sim e 'n' para não: ")
        if response == "s":
            kp = float(input("Informe o valor de Kp: "))
            ki = float(input("Informe o valor de Ki: "))
            kd = float(input("Informe o valor de Kd: "))
            oven.pid.update_constants(kp, ki, kd)
        oven.intialize()
        oven.set_reference_temperature(reference_temperature)
        try:
            while True:
                oven.control_temperature()
                sleep(0.1)
        except KeyboardInterrupt:
            oven.down()
