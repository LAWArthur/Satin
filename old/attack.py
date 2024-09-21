from game import Skill, SkillFactory
from game import game

class Attack(Skill):
    def __init__(self, cost: int, player, target, attack: int, resistance: int, priority, tags=None) -> None:
        super().__init__(cost, player, target, priority, tags)
        self.attack = attack
        self.resistance = resistance

    @property
    def is_defense(self) -> bool:
        return False
    @property
    def is_single(self) -> bool:
        return False
    
    @property
    def is_attack(self) -> bool:
        return True
    
    def act(self, **kwargs):
        self.target.damage(self.player, self.attack, resistance='no_resistance' not in self.tags.keys())

class SaTin(Attack): # Satin结算实在有点复杂比较难划归到基础攻击类，寄
    def __init__(self, player, target, sa, tin, tags=None) -> None:
        super().__init__(sa + tin, player, target, sa + 3 * tin, 5 * sa + tin, 1, tags)
        self.sa = sa
        self.tin = tin
        self.tags['name'] = f'sa{sa}tin{tin}'

    @property
    def is_defense(self) -> bool: # satin有特殊防御结算机制
        return len(self.player.sequence) == 1 # 仅当只出satin时有效

    def act(self, **kwargs):
        if 'attack' in kwargs.keys(): # 防守方
            attack = kwargs['attack']
            if isinstance(attack, SaTin):
                
                # 纯sa纯tin的case
                if(self.sa == 0 and attack.tin == 0):
                    self.player.damage(attack.player, attack.sa, resistance=False)
                    return True
                elif self.tin == 0 and attack.sa == 0:
                    self.player.heal(attack.tin)
                    return True
                # 其他case
                else:
                    return False

            else: return False

        else: # 进攻方
            super().act(**kwargs)

class AttackFactory(SkillFactory):
    def __init__(self, cost: int, player, targets, priority, resistance, tags=None) -> None:
        super().__init__(cost, player, targets, priority, tags)
        self.resistance = resistance
    @property
    def is_single(self) -> bool:
        return False
    @property
    def is_defense(self) -> bool:
        return False
    @property
    def is_attack(self) -> bool:
        return True

class Jianyu(AttackFactory):
    def __init__(self, player, tags=None) -> None:
        super().__init__(2, player, Game.game.get_other_players(player), 1, 2, tags)
        self.tags['name'] = 'jianyu'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 2, 2, 1, self.tags) for i in self.targets]

class Nanman(AttackFactory):
    def __init__(self, player, targets, tags=None) -> None:
        super().__init__(3, player, targets, 1, 5, tags)
        self.tags['no_normal_defense'] = 'no_normal_defense'
        self.tags['name'] = 'nanman'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 3, 5, 1, self.tags) for i in self.targets]

class Wanjian(AttackFactory):
    def __init__(self, player, targets, tags=None) -> None:
        super().__init__(3, player, targets, 1, 5, tags)
        self.tags['no_pass'] = 'no_pass'
        self.tags['name'] = 'wanjian'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 2, 5, 1, self.tags) for i in self.targets]

class Lightning(AttackFactory):
    def __init__(self, player, targets, tags=None) -> None:
        super().__init__(4, player, targets, 1, 5, tags)
        self.tags['no_normal_defense'] = 'no_normal_defense'
        self.tags['name'] = 'lightning'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 4, 5, 1, self.tags) for i in self.targets]
    
class Huowu(AttackFactory):
    def __init__(self, player, targets, tags=None) -> None:
        super().__init__(5, player, targets, 1, 5, tags)
        self.tags['no_normal_defense'] = 'no_normal_defense'
        self.tags['name'] = 'huowu'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 5, 5, 1, self.tags) for i in self.targets]

class Hebao(AttackFactory):
    def __init__(self, player, targets, tags=None) -> None:
        super().__init__(6, player, targets, 1, 6, tags)
        self.tags['can_bing'] = 'can_bing'
        self.tags['no_defense'] = 'no_defense'
        self.tags['no_resistance'] = 'no_resistance'
    
    def construct(self) -> list[Skill]:
        return [Attack(self.cost, self.player, i, 6, 6, 1, self.tags) for i in self.targets]