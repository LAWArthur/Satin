from game import Skill
from abc import abstractmethod
from game import Game

class Defense(Skill):
    def __init__(self, cost: int, player, priority, tags = None) -> None:
        super().__init__(cost, player, None, priority, tags)
    
    @property
    def is_defense(self) -> bool:
        return True
    
    @property
    def is_attack(self) -> bool:
        return False
    
    @abstractmethod
    def act(self, attack: Skill, **kwargs) -> bool:
        pass

    @property
    def is_single(self) -> bool:
        return True

class Defense_Normal(Defense):
    def __init__(self, player, tags=None) -> None:
        super().__init__(0, player, 1, tags)
    
    def act(self, attack: Skill, **kwargs) -> bool:
        return 'no_normal_defense' not in attack.tags.keys() and 'no_defense' not in attack.tags.keys()

# 理论上任何攻击手段都可以防
class Defense_T(Defense):
    def __init__(self, player, type, tags=None) -> None:
        super().__init__(0, player, 1, tags)
        self.type = type

    def act(self, attack: Skill, **kwargs) -> bool:
        return 'name' in attack.tags.keys() and attack.tags['name'] == self.type and 'no_defense' not in attack.tags.keys()

class Pass(Defense):
    def __init__(self, player, target, tags=None) -> None:
        super().__init__(player.cost if player.cost > 0 else 1, player, 1, tags)
        self.target = target
    
    def act(self, attack: Skill, **kwargs) -> bool:
        if 'no_pass' in attack.tags.keys() or 'no_defense' in attack.tags.keys(): return False

        if 'pass_count' not in attack.tags.keys():
            attack.tags['pass_count'] = 0
        attack.tags['pass_count'] += 1
        if attack.tags['pass_count'] >= Game.game.player_num: # 成环，攻击消失
            return True
        
        attack.target = self.target # 重定向
        
        if attack.player != attack.target: return attack.target.act_defense(attack)
        else: # pass到发出者时不计防御
            attack.tags['no_resistance'] = 'no_resistance'
            attack.tags['no_defense'] = 'no_defense'
            return False 

class Bing(Defense): # 根据先辈的写法饼也是防御手段，合理
    def __init__(self, player, tags=None) -> None:
        super().__init__(-1, player, 1, tags)
    
    def act(self, attack: Skill, **kwargs) -> bool:
        return 'can_bing' in attack.tags.keys() # 饼不受 no_defense 标签控制