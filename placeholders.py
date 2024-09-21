import game

class Placeholder:
    def value(self, *args, **kwargs):
        pass

    def __add__(self, other):
        return Add(self, other)

class Add(Placeholder):
    def __init__(self, a, b) -> None:
        self.a = a if isinstance(a, Placeholder) else Const(a)
        self.b = b if isinstance(b, Placeholder) else Const(b)
    def value(self, *args, **kwargs):
        return self.a.value(*args, **kwargs) + self.b.value(*args, **kwargs)
        
class Const(Placeholder):
    def __init__(self, v) -> None:
        self.v = v
    def value(self, *args, **kwargs):
        return self.v

class Player(Placeholder):
    def __init__(self, p = None, default = None) -> None:
        self.p = p
        self.default = default

    def value(self, matches, player: game.Player, *args, **kwargs) -> game.Player:
        raw = None
        if self.p is not None: raw = matches.group(self.p)
        if isinstance(raw, str) and raw.isdecimal():
            pid = int(raw) - 1
            return game.Game.game.players[pid]
        elif self.default is None:
            return player
        else:
            return self.default
        
class Players(Placeholder):
    def __init__(self, p = None, default = None) -> None:
        self.p = p
        self.default = default
    def value(self, matches, player: game.Player, *args, **kwargs) -> list[game.Player]:
        raw = None
        if self.p is not None: raw = matches.group(self.p)
        if isinstance(raw, str) and raw.isdecimal():
            pid = int(raw) - 1
            return [game.Game.game.players[pid]]
        elif self.default is None:
            return [player]
        elif self.default == 'all':
            return player.get_other_players()
        else:
            return self.default
        
        
class Int(Placeholder):
    def __init__(self, p = None, default = 0) -> None:
        self.p = p
        self.default = default
    
    def value(self, matches, *args, **kwargs):
        raw = None
        if self.p is not None: raw = matches.group(self.p)
        if isinstance(raw, str) and raw.isdecimal():
            return int(raw)
        else:
            return self.default
        
class Len(Placeholder):
    def __init__(self, p = None, default = 0) -> None:
        self.p = p
        self.default = default
    
    def value(self, matches, *args, **kwargs):
        raw = None
        if self.p is not None: raw = matches.group(self.p)
        if isinstance(raw, str):
            return len(raw)
        else:
            return self.default
