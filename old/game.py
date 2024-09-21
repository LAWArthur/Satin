from abc import ABC, abstractmethod
from types import *
from functools import reduce


"""
所有的出招可分为三类：
一类：普通攻击类，可完全规约为对单体的 Attack
二类：防御类，相当于对攻击的筛
三类：其他，有特殊结算规则（故通常不受防御和防值影响）
"""

class Skill(ABC):
    def __init__(self, cost: int, player, target, priority, tags = None) -> None:
        self.cost = cost
        self.player: Player = player # 当前角色
        self.target: Player = target
        self.priority = priority
        self.tags = tags if tags != None else dict()
    
    # 二类出招（防御）会进入防御序列而不会进入攻击序列
    @property
    @abstractmethod
    def is_defense(self) -> bool:
        pass
    
    # 是否只允许单独出招
    @property
    @abstractmethod
    def is_single(self)-> bool:
        pass
    
    @property
    @abstractmethod
    def is_attack(self) -> bool:
        pass

    @abstractmethod
    def act(self, **kwargs):
        pass

    def after_phase(self):
        pass

class SkillFactory(ABC):
    def __init__(self, cost: int, player, targets, priority, tags = None) -> None:
        self.cost = cost
        self.player = player # 当前角色
        self.targets = targets
        self.priority = priority
        self.tags = tags if tags != None else dict()

    @abstractmethod
    def construct(self) -> list[Skill] :
        pass
    
    @property
    @abstractmethod
    def is_single(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_defense(self) -> bool:
        return False
    
    @property
    @abstractmethod
    def is_attack(self) -> bool:
        pass

class Overflow(Skill): # 爆点
    def __init__(self, player, tags=None) -> None:
        super().__init__(0, player, player, 100, tags)
    def act(self, **kwargs):
        self.player.damage(self.player, 3, resistance=False)
        Game.game.force_end()
    @property
    def is_defense(self):
        return False
    @property
    def is_single(self):
        return False
    @property
    def is_attack(self):
        return True

class Game:
    game = None

    @staticmethod
    def make_game(n, hp):
        Game.game: Game = Game(n, hp)

    def __init__(self, n, hp) -> None:
        self.players = [Player(hp) for i in range(n)]
        self._damaged = False
        self._endphase = False
        self.sequence: dict[int, list[Skill]] = dict()

    @property
    def player_num(self) -> int:
        return len(self.players)
    
    def get_other_players(self, player):
        return [i for i in self.players if i != player]
    
    def set_damaged(self):
        self._damaged = True

    def force_end(self):
        self._endphase = True

    def enqueue(self, skill: Skill):
        if skill.priority not in self.sequence.keys():
            self.sequence[skill.priority] = list()
        self.sequence[skill.priority].append(skill)

    def begin_game(self):
        self.round_begin()
        self.phase_clear()

    def round_begin(self):
        self._damaged = False
        for i in self.players:
            i.round_begin()

    def round_end(self):
        for i in self.players:
            pass
    
    def phase_clear(self):
        self.sequence = dict()
        for i in self.players:
            i.phase_clear()
    
    def phase(self):
        for i in self.players:
            i.phase_begin()
        
        print(self.sequence)

        for i in sorted(self.sequence.keys(), reverse=True):
            for j in self.sequence[i]:
                if not j.target.act_defense(j):
                    j.act()
            if self._endphase:
                break
        
        for i in self.players:
            i.phase_end()

        if self._damaged:
            self.round_end()
            self.round_begin()

        self.phase_clear()

class Player:
    def __init__(self, hp: int) -> None:
        self._hp = hp
        self._sequence: list = None
        self.cost = 0
        self.cur_cost = 0
        self.defense = None


    def __repr__(self) -> str:
        return f'hp: {self.hp}  cost: {self.cost}'
    
    def round_begin(self):
        self.cost = 0
    
    def phase_clear(self):
        self._sequence = None
        self.damage_list: dict[Player, list[Skill]] = dict()
        self.defense = None

    def phase_end(self):
        self.cost -= self.cur_cost
        for i in self.damage_list:
            #TODO
            pass

    def phase_begin(self):
        self.enqueue(self.sequence)

    @property
    def hp(self):
        return self._hp
    
    @hp.setter
    def hp(self, value):
        Game.game.set_damaged()
        self._hp = value

    @property
    def sequence(self):
        return self._sequence
    
    def enqueue(self, seq):
        if isinstance(seq, list):
            for i in seq:
                self.enqueue(i)
        elif isinstance(seq, Skill):
            if seq.is_defense: self.defense = seq
            if seq.is_attack: Game.game.enqueue(seq)
        elif isinstance(seq, SkillFactory):
            self.enqueue(seq.construct())

    @sequence.setter
    def sequence(self, value: list[Skill]):
        # 检验cost
        cost = reduce(lambda res, i: res + i.cost, value, 0)
        if cost > self.cost:
            self._sequence = [Overflow(self)]
            self.cur_cost = 0
            return
        
        # 检验出招合法性
        for i in value:
            if i.is_single and len(value) > 1:
                self._sequence = [Overflow(self)]
                self.cur_cost = 0
                return
        
        self._sequence = value

        self.cur_cost = cost

    def damage(self, origin, amount: int, resistance = True):
        if resistance:
            #TODO
            pass
        else: # 直接结算
            self.hp -= amount
    
    def heal(self, amount: int):
        self.hp += amount
    
    def act_defense(self, skill: Skill) -> bool:
        return self.defense.act(attack = skill) if self.defense is not None else False
    


game: Game = Game(3, 6)