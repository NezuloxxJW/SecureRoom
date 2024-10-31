__DEBUG__ = True
def DbgPrint(string: str, color: str = "default"):
    # Define color codes
    colors = {
        "default": "\033[0m",  # Default color
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    # Get the color code, default to "default" if not recognized
    color_code = colors.get(color, colors["default"])
    
    # Print the colored string
    if __DEBUG__:
        print(f"{color_code}{string}\033[0m")  # Reset color after printing