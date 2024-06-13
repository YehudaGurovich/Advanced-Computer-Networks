def open_file(file_path: str) -> list:
    data: list = []
    with open(file_path, "r") as file:
        for line in file:
            data.append(line.strip())

    return data


def main():
    print(open_file("combined_wordlist.txt"))


if __name__ == "__main__":
    main()
