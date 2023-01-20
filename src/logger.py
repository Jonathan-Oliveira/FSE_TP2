import csv
from datetime import datetime
import os


class Logger:
    def __init__(self):
        self.file_name = "log.csv"
        if not os.path.isfile(self.file_name):
            with open(self.file_name, "w") as f:
                f.write(
                    "Data e hora,temperatura interna,temperatura externa,temperatura definida pelo usuário, Atuador Resistor, Atuador Ventoinha)\n"
                )

    def write_log(
        self,
        internal_temperature,
        ambiente_temperature,
        reference_temperature,
        control_signal,
    ):
        if control_signal > 0:
            fan = 0
            resistor = abs(control_signal)
        else:
            fan = abs(control_signal)
            resistor = 0

        log_data = [
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            internal_temperature,
            ambiente_temperature,
            reference_temperature,
            resistor,
            fan,
        ]
        with open(self.file_name, mode="a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(log_data)
