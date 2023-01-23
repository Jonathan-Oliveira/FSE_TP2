from oven import Oven
from time import sleep
from menu import Menu

if __name__ == "__main__":

    # Create a menu to select the mode
    menu = Menu()
    oven = Oven()
    commands = {
        "turn_on_oven": oven.turn_on,
        "turn_off_oven": oven.turn_off,
        "turn_on_heating": oven.start_heating,
        "turn_off_heating": oven.stop_heating,
        "change_mode": oven.change_mode,
    }
    comands_debug = {
        "update_reference_temperature": menu.ask_for_reference_temperature,
        "update_constants": menu.ask_for_constants,
    }
    set_commands = {
        "internal_temperature": oven.set_internal_temperature,
        "reference_temperature": oven.set_reference_temperature,
    }
    commands_debug = {**commands, **comands_debug}
    sleep(1)
    mode = menu.select_mode()
    oven.intialize()
    try:
        while mode != 4:
            if mode == 1:
                print("Modo dashboard selecionado...")
                oven.udpate_system_mode("dashboard")
                while True:
                    oven.uart.send("get_user_command")
                    oven.receive()
                    if oven.is_on and oven.is_heating:
                        oven.control_temperature()
                    sleep(0.5)
            elif mode == 2:
                oven.udpate_system_mode("debug")
                oven.set_mode("curve")
                if not oven.is_on:
                    oven.turn_on()
                if not oven.is_heating:
                    oven.start_heating()

            elif mode == 3:
                print("Modo debug selecionado...")
                oven.udpate_system_mode("debug")
                reference_temperature = menu.ask_for_reference_temperature()
                oven.update_reference_temperature(reference_temperature)
                kp, ki, kd = menu.ask_for_constants()
                oven.pid.update_constants(kp, ki, kd)
                # menu.clear_screen()
                while True:
                    user_command = menu.select_debug_command()
                    if user_command == "update_reference_temperature":
                        value_user = commands_debug.get(user_command, oven.empty)()
                        oven.set_reference_temperature(value_user)
                        continue
                    elif user_command == "update_constants":
                        oven.pid.update_constants(*value_user)
                    elif user_command == "change_mode":
                        oven.change_mode()
                        continue
                    commands_debug.get(user_command, oven.empty)()
                    sleep(0.1)

            mode = menu.select_mode()
    except KeyboardInterrupt:
        try:
            oven.down()
        except Exception:
            pass
        finally:
            print("Saindo do programa...")
            exit()
