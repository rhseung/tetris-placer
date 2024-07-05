class SingleTon:
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingleTon, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def darken_color(color: int, ratio: float = 0.5) -> int:
    r = color >> 16
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    
    return (int(r*ratio) << 16) + (int(g*ratio) << 8) + int(b*ratio)