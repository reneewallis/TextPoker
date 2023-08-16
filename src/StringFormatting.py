def printPaddedInBox(string, boxChar, padding=2):
    boxSize = len(string) + 4
    print(boxChar * boxSize)
    for i in range(2):
        for _ in range(padding):
            print(boxChar, " " * (boxSize - 4), boxChar)
        if i == 1:
            break
        print(boxChar, string, boxChar)
    print(boxChar * boxSize)


def printInFancyBox(msg, indent=1, width=None, title=None):
    lines = msg.split("\n")
    space = " " * indent
    if not width:
        width = max(map(len, lines))

    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f"║{space}{title:<{width}}{space}║\n"  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += "".join([f"║{space}{line:^{width}}{space}║\n" for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)


def borderedText(lines):
    if type(lines) == str:
        lines = lines.splitlines()
    width = max(len(line) for line in lines)
    result = ["┌" + "─" * width + "┐"]
    for line in lines:
        result.append("│" + (line + " " * width)[:width] + "│")
    result.append("└" + "─" * width + "┘")
    text = "\n".join(result)

    print(text)


def padAndCentreLine(line, width):
    lineLength = len(line)
    padding = width - lineLength if lineLength < width else 0
    padding = padding // 2
    print("~" * padding + " " + line + " " + "~" * padding)


def printWithSeperators(lines, sepChar):
    lines = lines.splitlines()
    print("\n")
    width = max(map(len, lines))
    print(sepChar * width)
    for line in lines:
        print(line)
    print(sepChar * width, end="\n\n")
