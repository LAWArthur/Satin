from game import Defense, Game, Skill, Player
import logging

class Bing(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, [player], 0, 0)
    
    def postphase(self):
        self.player.cost += 1

class SaTin(Skill):
    def __init__(self, player: Player, targets: list[Player], sa: int, tin: int) -> None:
        super().__init__(player, targets, sa + 3 * tin, sa + tin)
        self.sa = sa
        self.tin = tin
    
    @staticmethod
    def is_pure_satin(player: Player, target: Player):
        ap = player.get_attacks_preview(target)
        return len(ap) == 1 and isinstance(ap[0], SaTin) and ap[0].sa * ap[0].tin == 0

    def prephase_500(self):
        if SaTin.is_pure_satin(self.player, self.targets[0]) and SaTin.is_pure_satin(self.targets[0], self.player):
            self.no_resistance = True

    def get_resistance(self, source: Player):
        if source not in self.targets: return 0
        if SaTin.is_pure_satin(self.player, source) and SaTin.is_pure_satin(source, self.player): return 0
        return 5 * self.sa + 1 * self.tin
    
    def phase_500(self, target:Player):
        if target == self.player: # 特判打自己
            target.hp -= self.attack
            return
        if SaTin.is_pure_satin(self.player, target):
            if SaTin.is_pure_satin(target, self.player): # 纯sa打纯tin规则
                other: SaTin = target.get_attacks_preview(self.player)[0]
                if self.sa != 0 and other.tin != 0:
                    target.hp -= self.sa
                elif self.tin != 0 and other.sa != 0:
                    target.hp += self.tin
                elif self.sa != 0 and other.sa != 0:
                    if self.sa > other.sa: target.hp -= self.sa - other.sa
                else:
                    if self.tin > other.tin: target.hp -= 3 * (self.tin - other.tin)
                return

            elif self.tin != 0: # tin 费用规则
                tcost = sum([s.cost for s in target.get_attacks_preview(self.player)])
                logging.info(tcost)
                if tcost < self.tin:
                    target.hp -= self.attack
                return
        target.hp -= self.attack

    def can_merge(self, other: Skill):
        return isinstance(other, SaTin) and other.player == self.player and other.targets[0] == self.targets[0]
    
    def merge(self, other: 'SaTin'):
        self.sa += other.sa
        self.tin += other.tin
        self.cost = self.sa + self.tin
        self.attack = self.sa + 3 * self.tin

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sa={self.sa},tin={self.tin})'

class NormalDefense(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 0, 0)
        self.no_defense = True

    class NormalDefense_Defense(Defense):
        def __init__(self, player, source) -> None:
            super().__init__(player, source, self, 0)
        def defend(self, skill: Skill):
            return not hasattr(skill, 'no_normal_defense')

    def get_defense(self, source: Player):
        return NormalDefense.NormalDefense_Defense(self.player, source)

class Pass(Skill):
    def __init__(self, player: Player, target: Player) -> None:
        super().__init__(player, [target], 0, player.cost if player.cost > 0 else 1)
        self.target = target
        self.no_defense = True
    
    @staticmethod
    def is_pass(player: Player):
        return len(player.sequence) == 1 and isinstance(player.sequence[0], Pass)

    def prephase_800(self):
        game = Game.game
        count = 0
        while count < game.nplayers and self.target is not None and Pass.is_pass(self.target):
            self.target = self.target.sequence[0].target
            count += 1
        if self.target is not None and Pass.is_pass(self.target): self.target = None

    def prephase_700(self):
        game = Game.game
        for p in game.players:
            for s in p.sequence:
                if not isinstance(s, Pass) and not hasattr(s, 'no_pass') and self.player in s.targets:
                    s.targets = [t if t is not self.player else self.target for t in s.targets if t is not self.player or self.target is not None]

class Barbarian(Skill):
    def __init__(self, player: Player, targets: list[Player] = None) -> None:
        super().__init__(player, targets if targets is not None else player.get_other_players(), 3, 3)
        self.no_normal_defense = True
    
    def get_resistance(self, source: Player):
        if source in self.targets:
            return 3
        return 0
    
    def phase_500(self, target: Player):
        target.hp -= self.attack
    
class Lightning(Skill):
    def __init__(self, player: Player, targets: list[Player] = None) -> None:
        super().__init__(player, targets if targets is not None else player.get_other_players(), 4, 4)
        self.no_normal_defense = True
    
    def get_resistance(self, source: Player):
        if source in self.targets:
            return 4
        return 0
    
    def phase_500(self, target: Player):
        target.hp -= self.attack

class ShiranuiMai(Skill):
    def __init__(self, player: Player, targets: list[Player] = None) -> None:
        super().__init__(player, targets if targets is not None else player.get_other_players(), 5, 5)
        self.no_normal_defense = True
    
    def get_resistance(self, source: Player):
        if source in self.targets:
            return 5
        return 0
    
    def phase_500(self, target: Player):
        target.hp -= self.attack

class Defense_T(Skill):
    def __init__(self, player: Player, T: type) -> None:
        super().__init__(player, [], 0, 0)
        self.t = T
        self.no_defense = True
    
    class Defense_T_Defense(Defense):
        def __init__(self, player, source, T: type) -> None:
            super().__init__(player, source, self, 0)
            self.t = T
        
        def defend(self, skill: Skill):
            return isinstance(skill, self.t)
    
    def get_defense(self, source: Player):
        return Defense_T.Defense_T_Defense(self.player, source, self.t)
    
class ArrowRain(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 2, 2)
    
    def get_resistance(self, source: Player):
        if source in self.targets:
            return 2
        return 0
    
    def phase_500(self, target: Player):
        target.hp -= self.attack

class LargeArrowRain(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 2, 3)
        self.no_pass = True
    
    def get_resistance(self, source: Player):
        if source in self.targets:
            return 3
        return 0
    
    def phase_500(self, target: Player):
        target.hp -= self.attack

class Suicide(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, [player], 1, 0)
        self.no_defense = True

    def phase_600(self, target: Player):
        target.hp -= 1
        Game.game.force_end_phase()

    @staticmethod
    def is_suicide(player: Player):
        return len(player.sequence) == 1 and isinstance(player.sequence[0], Suicide)

class AntiSuicide(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 7, 0)
        self.no_defense = True
        # self.origin = self
        self.aha = False
    
    def phase_700(self, target:Player):
        if Suicide.is_suicide(target):
            target.hp -= 7
            self.origin.aha = True
        Game.game.force_end_phase()
    
    def postphase(self):
        if not self.aha:
            self.player.hp -= 7

class BaSa(Skill):
    def __init__(self, player: Player, target: Player) -> None:
        super().__init__(player, [target], 8, 8)
        self.no_defense = True

    def get_resistance(self, source: Player):
        if source in self.targets:
            return 10000
        return 0

    def phase_1100(self, target: Player):
        target.hp -= 8

class Lona(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, [], 0, 3)
        self.no_defense = True
    
    class Lona_Defense(Defense):
        def __init__(self, player, source) -> None:
            super().__init__(player, source, self, 0)
            self.override_BaSa = True
        def defend(self, skill: Skill):
            return isinstance(skill, BaSa)
    
    def get_defense(self, source: Player):
        return Lona.Lona_Defense(self.player, source)
    
class NuclearBomb(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 6, 6)
        self.no_defense = True
    
    def phase_800(self, target: Player):
        if len(target.sequence) == 1 and isinstance(target.sequence[0], Bing):
            pass
        else:
            target.hp -= 6
        Game.game.force_end_phase()

class EndOfAll(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, player.get_other_players(), 30, 14)
        self.no_defense = True
    
    def phase_1200(self, target: Player):
        target.hp -= 30
        Game.game.force_end_phase()

class Peach(Skill):
    def __init__(self, player: Player, target: Player, num: int) -> None:
        super().__init__(player, [target], 0, 3 * num)
        self.num = num
        self.has_defended = False
    
    class Peach_Defense(Defense):
        def __init__(self, player, source, origin: 'Peach') -> None:
            super().__init__(player, source, self, -1)
            self.origin = origin
            self.no_defense = True

        def defend(self, skill: Skill):
            self.origin.has_defended = True
            return True
    
    def get_defense(self, source: Player):
        return Peach.Peach_Defense(self.player, source, self)

    def postphase(self):
        print('ok!')
        self.player.hp += (self.num if not self.has_defended else self.num - 1)

    def can_merge(self, other: Skill):
        return isinstance(other,Peach) and other.player == self.player and other.targets[0] == self.targets[0]
    
    def merge(self, other: 'Peach'):
        self.num += other.num
        self.cost = self.num * 3
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.num})'