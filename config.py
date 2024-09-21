from game import *
from skills import *
import re
import placeholders as p


config = {
    'nplayers': 3,
    'hp': 6,
    'allowed_skills':[
        {
            'skill': Bing,
            'pattern': r'<key_bing>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': BaSa,
            'pattern': r'([0-9]+)<key_sa>8',
            'parameters': [p.Player(), p.Player(1)],
            'single': True
        },
        {
            'skill': SaTin,
            'pattern': r'([0-9]+)(((<key_sa>+)([0-9]*))((<key_tin>+)([0-9]*))?|((<key_tin>+)([0-9]*)))',
            'parameters': [p.Player(), p.Players(1), p.Len(4)+p.Int(5,1)+(-1), p.Len(7)+p.Int(8,1)+(-1) + p.Len(10)+p.Int(11,1)+(-1)],
            'single': False
        },
        {
            'skill': NormalDefense,
            'pattern': r'<key_ndefense>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': Pass,
            'pattern': r'([0-9]+)<key_pass>',
            'parameters': [p.Player(),p.Player(1)],
            'single': True
        },
        {
            'skill': Barbarian,
            'pattern': r'([0-9]*)<key_barbarian>',
            'parameters': [p.Player(),p.Players(1, 'all')],
            'single': False
        },
        {
            'skill': Lightning,
            'pattern': r'([0-9]*)<key_lightning>',
            'parameters': [p.Player(),p.Players(1, 'all')],
            'single': False
        },
        {
            'skill': ShiranuiMai,
            'pattern': r'([0-9]*)<key_mai>',
            'parameters': [p.Player(),p.Players(1, 'all')],
            'single': False
        },
        {
            'skill': ArrowRain,
            'pattern': r'<key_arrowrain>',
            'parameters': [p.Player()],
            'single': False
        },
        {
            'skill': ArrowRain,
            'pattern': r'<key_larrowrain>',
            'parameters': [p.Player()],
            'single': False
        },
        {
            'skill': LargeArrowRain,
            'pattern': r'<key_larrowrain>',
            'parameters': [p.Player()],
            'single': False
        },
        {
            'skill': Defense_T,
            'pattern': r'<key_ndefense><key_barbarian>',
            'parameters': [p.Player(), p.Const(Barbarian)],
            'single': True
        },
        {
            'skill': Defense_T,
            'pattern': r'<key_ndefense><key_lightning>',
            'parameters': [p.Player(), p.Const(Lightning)],
            'single': True
        },
        {
            'skill': Defense_T,
            'pattern': r'<key_ndefense><key_mai>',
            'parameters': [p.Player(), p.Const(ShiranuiMai)],
            'single': True
        },
        {
            'skill': Suicide,
            'pattern': r'<key_suicide>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': AntiSuicide,
            'pattern': r'<key_antisuicide>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': Overflow,
            'pattern': r'<key_overflow>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': Lona,
            'pattern': r'<key_lona>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': NuclearBomb,
            'pattern': r'<key_bomb>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': EndOfAll,
            'pattern': r'<key_endofall>',
            'parameters': [p.Player()],
            'single': True
        },
        {
            'skill': Peach,
            'pattern': r'(<key_peach>+)([1-9][0-9]*)?',
            'parameters': [p.Player(), p.Player(), p.Len(1) + p.Int(2)],
            'single': True
        }
    ],
    'key_binds':{
        'key_bing': 'a',
        'key_sa': 's',
        'key_tin': 'd',
        'key_ndefense':'f',
        'key_pass':'q',
        'key_barbarian': 'e',
        'key_lightning': 'g',
        'key_mai': 'h',
        'key_arrowrain':'r',
        'key_larrowrain': 'w',
        'key_suicide': 'z',
        'key_antisuicide': 'x',
        'key_overflow': 'c',
        'key_lona': 'l',
        'key_bomb': 'v',
        'key_endofall': 'juesha',
        'key_peach': 't'
    }
}