def format_number(n, decimal=2):
    suffixes = ["", "mil", "mi", "bi", "tri", "quad", "quint", "sext", "sept", "oct", "non", "dec"]
    
    sign = "-" if n < 0 else ""
    n = abs(n)

    index = 0
    while n >= 1000 and index < len(suffixes) - 1:
        n /= 1000.0
        index += 1
    
    return f"{sign}{n:.{decimal}f} {suffixes[index]}".strip()