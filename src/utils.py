from csv import reader


def load_csv():
    """
    Load csv file and return a list of dictionaries

    example:
    {0: 25,60: 38, 120: 46, 240:54, 260:57, 300:61, 360:63, 420:54, 480:33, 600:25 }
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
        temperature = float(row[1].rstrip())
        data.update({time: temperature})

    return data


if __name__ == "__main__":
    data = load_csv()
    print(data)
    print(data.get(0))
