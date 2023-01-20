from csv import reader


def load_csv():
    """
    Load csv file and return a list of dictionaries

    example:
    [{"time": 0, "temperature": 25}, {"time": 1, "temperature": 38}, ...}]
    """
    data = dict()
    # Open file in read mode
    file = open("src/curva_reflow.csv", "r")
    # Reading file
    csv_reader = reader(file)
    for row in csv_reader:
        if ["Tempo (s)", " Temperatura"] == row:
            continue
        if not row:
            continue
        time = int(row[0].rstrip())
        temperature = int(row[1].rstrip())
        data.update({time: temperature})

    return data


if __name__ == "__main__":
    data = load_csv()
    print(data)
