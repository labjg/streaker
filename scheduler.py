#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Lines In Space (LIS) scheduler
# Designed to be run every 24 hours with cron.
# Requires rclone with a configured remote, defined below.
# By James Gilbert (@labjg) 2018-08; feel free to take, use, fix, hack etc.

import os
import glob
import random
import streaker
import time
import pub

REMOTE_NAME = 'dropbox'
REMOTE_DIR = 'Apps/lines_in_space/images/'
LOCAL_DIR = '/home/pi/lines_in_space/images/'
TODO_DIR = 'in/todo/'
DONE_DIR = 'in/done/'
OUT_DIR = 'out/'

# The first thing to do is sync the LIS Dropbox to get any new source images.
try:
    os.system('rclone sync'
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR+TODO_DIR
              + ' ' + LOCAL_DIR+TODO_DIR )
except:
    pass

# Everything from this point is contingent on there being new source images
# available, and whether the selected image is processed successfully.
try:
    # We see whether there are any source images available for processing. If
    # so, one is picked at random, processed, and saved.
    infileList = glob.glob(LOCAL_DIR+TODO_DIR+'**/*.jpg')
    infilePath = random.choice(infileList)
    infileName = os.path.split(infilePath)
    outfilePath = LOCAL_DIR+OUT_DIR+infileName,
    vertical = os.path.split(infileName) == 'vertical'
    streaker.streak(
        infileChoice,
        outfilePath,
        vertical,
        rMedian = 0,
        contrast=1.5,
        saturatiokn=1.0,
        verbose=0 )

    # If we get this far then the image has been successully processed and
    # saved. Now we move the source file to the 'done' folder, sync with the
    # cloud, then pick a random delay before publishing in the next 24 hours.
    os.rename(infilePath, LOCAL_DIR+DONE_DIR+infileName)

    try:
        os.system('rclone sync'
              + ' ' + LOCAL_DIR+OUT_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR+OUT_DIR )
        os.system('rclone sync'
              + ' ' + LOCAL_DIR+TODO_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR+TODO_DIR )
        os.system('rclone sync'
              + ' ' + LOCAL_DIR+DONE_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR+DONE_DIR )
    except:
        pass

    randelay = random.randint(0,60*60*24)
    time.sleep(randelay)

    title = os.path.splitext(infileName)[0]
    #pub.tweet(outfilePath, title)


except:
    pass

# sync to cloud: todo, done, out

