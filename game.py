from typing import Any
from copy import copy,deepcopy
import inspect
import re
import logging

logging.basicConfig(filename='game.log', level=logging.INFO)

class Game:
    def __init__(self, config) -> None:
        self.nplayers = config['nplayers']
        self.hp = config['hp']
        self.config = deepcopy(config)
        self.players = [Player(i+1, self.hp) for i in range(self.nplayers)]
        self.is_end_round = False
        self.is_force_end_phase = False
        self.alive_players = copy(self.players)
        self.ranking = []
        self.finish = False
        self.msgdispatcher = MessageDispatcher()
        self.compile_config()

    def compile_config(self):
        config = self.config
        for c in config['allowed_skills']:
            rep = config['key_binds']
            pat: str = '^' + c['pattern'] + ('$' if c['single'] else '')
            for k,v in rep.items():
                pat = pat.replace(f'<{k}>', v)
            logging.info(pat)
            c['pattern'] = re.compile(pat)

    def convert_sequence(self, player: 'Player', seq: str):
        res: list['Skill'] = []
        seq = seq.strip()
        while seq != '':
            flag = False
            for c in self.config['allowed_skills']:
                pat: re.Pattern = c['pattern']
                m = pat.match(seq)
                logging.info((pat.pattern, m))
                if m is not None:
                    flag = True
                    s = c['skill'](*[p.value(m, player) for p in c['parameters']])
                    flag2 = False
                    for t in res:
                        if t.can_merge(s):
                            t.merge(s)
                            flag2 = True
                            break
                    if not flag2: res.append(s)
                    seq = seq[m.end():].strip()
                    break
            if not flag:
                res = [Overflow(player)]
                break
        
        player.sequence = res

    def set_game(self):
        Game.game = self

    def round_reset(self):
        self.is_end_round = False
        for p in self.players:
            p.round_reset()
    
    def on_prephase(self):
        self.is_force_end_phase = False
        for p in self.players: p.prephase()
        schedule: 'dict[int, list]' = dict()
        for p in self.players:
            for s in p.sequence:
                phasefuncs = [(name, value) for name, value in inspect.getmembers(s) if name.startswith('prephase_')]
                for name, value in phasefuncs:
                    try:
                        key = int(name[9:])
                    except ValueError:
                        continue
                    if key not in schedule.keys(): schedule[key] = list()
                    schedule[key].append((s, value))
        logging.info(schedule)
        keys = sorted(schedule.keys(), reverse=True)
        for k in keys:
            for s,f in schedule[k]:
                self.msgdispatcher.dispatch(SkillEffectMessage(s.player, s.targets, s, 'prephase_' + str(k)))
                f.__func__(s)
                

    def on_phase(self):
        schedule: 'dict[int, list]' = dict()
        for p in self.players:
            for t in self.players:
                atks = p.get_attacks(t)
                for s in atks:
                    phasefuncs = [(name, value) for name, value in inspect.getmembers(s) if name.startswith('phase_')]
                    for name, value in phasefuncs:
                        try:
                            key = int(name[6:])
                        except ValueError:
                            continue
                        if key not in schedule.keys(): schedule[key] = list()
                        schedule[key].append((s, t, value))
        logging.info(schedule)
        keys = sorted(schedule.keys(), reverse=True)
        for k in keys:
            for s,t,f in schedule[k]:
                self.msgdispatcher.dispatch(SkillEffectMessage(s.player, t, s, 'phase_' + str(k)))
                f.__func__(s,t)
                
            if self.is_force_end_phase: break

    def on_postphase(self):
        for p in self.players:
            p.postphase()

    def on_phase_reset(self):
        deaths = []
        for p in self.players:
            if not p.is_alive() and p in self.alive_players:
                self.alive_players.remove(p)
                deaths.append(p)
        if len(deaths) > 0: self.ranking.insert(0, deaths)
        
        for p in self.players:
            p.phase_reset()

        if self.is_end_round:
            self.round_reset()

    def phase(self):
        self.on_prephase()

        self.on_phase()

        self.on_postphase()

        self.on_phase_reset()
        
        if len(self.alive_players) <= 1:
            self.finish = True
            if len(self.alive_players) > 0:
                self.ranking.insert(0, copy(self.alive_players))

        return self.finish

        
    def force_end_phase(self):
        self.is_force_end_phase = True

    def end_round(self):
        self.is_end_round = True

class MessageDispatcher:
    def __init__(self) -> None:
        self.messages = []
    
    def dispatch(self, msg):
        self.messages.append(msg)
        print(msg)

    def clear(self):
        self.messages = []

class Message:
    def __repr__(self):
        return 'This message has not been implemented. '

class HPChangeMessage(Message):
    def __init__(self, player, change) -> None:
        super().__init__()
        self.player = player
        self.change = change
    def __repr__(self):
        return f'HP Change: {self.player} {self.change:+}'

class Player:
    def __init__(self, id, hp: int) -> None:
        self.id = id
        self._hp = hp
        self.cost = 0
        self.sequence: 'list[Skill]' = []

    @property
    def hp(self):
        return self._hp
    
    @hp.setter
    def hp(self, value):
        if self._hp == value: return
        Game.game.msgdispatcher.dispatch(HPChangeMessage(self, value - self._hp))
        self._hp = value
        Game.game.end_round() # 有血量变动即结束本轮
    
    def is_alive(self):
        return self.hp >= 0

    def get_other_players(self):
        return [p for p in Game.game.players if p != self and p.is_alive()]
    
    def get_defenses(self, source: 'Player'):
        if source == self: return list() # 自不设防
        res = [d for d in (s.get_defense(source) for s in self.sequence) if d is not None]
        res.append(Resistance(self, source, self.sequence))
        return sorted(res,reverse=True)
    
    def get_attacks(self, target: 'Player'):
        defenses = target.get_defenses(self)
        res = list()
        for s in self.sequence:
            res += [copy(s) for _ in range(s.targets.count(target))] # 被弹后会出现多重目标
        logging.info((self, res))
        for d in defenses:
            res = [s for s in res if (hasattr(s, 'no_defense') and not hasattr(d, 'override_' + type(s).__name__)) or not d(s)]
        return res
    
    def get_attacks_preview(self, target: 'Player') -> 'list[Skill]':
        res = list()
        for s in self.sequence:
            res += [copy(s) for _ in range(s.targets.count(target))]
        return res

    def round_reset(self):
        self.cost = 0

    def prephase(self):
        total_cost = sum([s.cost for s in self.sequence])
        if total_cost > self.cost:
            self.sequence = [Overflow(self)]
        else: self.cost -= total_cost

    def postphase(self):
        for s in self.sequence:
            s.postphase()
    
    def phase_reset(self):
        self.sequence = []
    
    def __repr__(self):
        return 'Player %d(hp=%d,cost=%d)'%(self.id, self.hp, self.cost)

class DefenseMessage(Message):
    def __init__(self, source, target, skilld, skilla) -> None:
        self.source = source
        self.target = target
        self.skilld = skilld
        self.skilla = skilla
    def __repr__(self):
        return f'Defense by {self.skilld}: {self.skilla}({self.source} -> {self.target})'

class Defense:
    def __init__(self, player, source, skill, priority: int) -> None:
        self.player = player
        self.source = source
        self.skill = skill
        self.priority = priority
    
    def __call__(self, skill: 'Skill'):
        res = self.defend(skill)
        if res:
            Game.game.msgdispatcher.dispatch(DefenseMessage(self.source, self.player, self.skill, skill))
        return res

    def defend(self, skill: 'Skill'):
        return False
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __repr__(self):
        return f'{self.__class__.__name__}'
    
class Resistance(Defense):
    def __init__(self, player, source, sequence: 'list[Skill]') -> None:
        super().__init__(player, source, self, -1000)
        self.resistance = sum((s.get_resistance(self.source) for s in sequence))
    
    def defend(self, skill: 'Skill'):
        if hasattr(skill,'no_resistance'): return False
        if skill.attack <= self.resistance:
            self.resistance -= skill.attack
            return True
        skill.attack -= self.resistance
        return False

class SkillEffectMessage(Message):
    def __init__(self, source, target, skill, phase) -> None:
        self.source = source
        self.target = target
        self.skill = skill
        self.phase = phase
    
    def __repr__(self):
        return f'Skill Effect: {self.skill}[{self.phase}]({self.source} -> {self.target})'

class Skill:
    def __init__(self, player: Player, targets: list[Player], attack:int, cost: int) -> None:
        self.player = player
        self.targets = targets
        self.attack = attack
        self.cost = cost
        self.origin = self
    
    def get_defense(self, source: Player) -> 'Defense | None':
        return None
    
    def get_resistance(self, source: Player):
        return 0

    def postphase(self):
        pass

    def can_merge(self, other: 'Skill'):
        return False
    
    def merge(self, other: 'Skill'):
        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}'

class Overflow(Skill):
    def __init__(self, player: Player) -> None:
        super().__init__(player, [player], 3, 0)

    def phase_1000(self, target: Player):
        target.hp -= 3
        Game.game.force_end_phase()