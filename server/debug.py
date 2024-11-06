__DEBUG__ = True
def DbgPrint(string: str, color: str = "default"):
    colors = {
        "default": "\033[0m", 
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    color_code = colors.get(color, colors["default"])
    
    if __DEBUG__:
        print(f"{color_code}{string}\033[0m")
