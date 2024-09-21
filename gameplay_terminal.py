from game import *
from skills import *
from config import config
import webbrowser,os

dir = os.path.dirname(__file__)
path = 'file:///' + os.path.join(dir, 'readme.html')
print(path)
webbrowser.open(path)

config['nplayers'] = int(input('Number of players:'))
config['hp'] = int(input('hp:'))

game = Game(config)
game.set_game()
players = game.players

def get_sequences():
    for p in players:
        if p.is_alive(): game.convert_sequence(p, input(p))
    for p in players:
        print(p.sequence)

'''
    游戏主循环，会一直运行到游戏结束
    每轮会依次跳出对话框，分别输入对应玩家的操作
    错误的操作会变成爆点
'''

get_sequences()
while(not game.phase()):
    print(players)
    get_sequences()
print(players)

print(game.ranking)