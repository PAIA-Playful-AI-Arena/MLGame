import pickle
from os import path

import numpy as np
# Fetch data
filename = path.join(path.dirname(__file__), 'log_template.pickle')
log = pickle.load((open(filename, 'rb')))

Frames = []
Balls = []
Commands = []
PlatformPos = []
sceneInfos = log['scene_info']
commands = log['command']

for sceneInfo in sceneInfos:
    Frames.append(sceneInfo['frame'])
    Balls.append([sceneInfo['ball'][0],sceneInfo['ball'][1]])
    # Commands.append(sceneInfo.command)
    PlatformPos.append(sceneInfo['platform'])

PlatX = np.array(PlatformPos)[:,0][:,np.newaxis]
# PlatX_next = PlatX[1:,:]

print(PlatX)