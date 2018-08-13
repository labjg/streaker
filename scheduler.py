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
#import pub

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
except Exception as e:
    print(e)

# Everything from this point is contingent on there being new source images
# available, and whether the selected image is processed successfully.
try:
    # We see whether there are any source images available for processing. If
    # so, one is picked at random, processed, and saved.
    infileList = glob.glob(LOCAL_DIR+TODO_DIR+'**/*.jpg')
    infilePath = random.choice(infileList)
    infileDir = os.path.split(infilePath)[0]
    infileName = os.path.split(infilePath)[1]
    infileSub = os.path.split(infileDir)[1]
    outfilePath = LOCAL_DIR+OUT_DIR+infileSub+'/'+infileName
    vertical = infileSub == 'vertical'
    streaker.streak(
        infilePath,
        outfilePath,
        vertical,
        rMedian = 0,
        contrast=1.5,
        saturation=1.0,
        verbose=0 )

    # If we get this far then the image has been successully processed and
    # saved. Now we move the source file to the 'done' folder, sync with the
    # cloud, then pick a random delay before publishing in the next 24 hours.
    os.rename(infilePath, LOCAL_DIR+DONE_DIR+infileSub+'/'+infileName)

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
    except Exception as e:
    print(e)

    randelay = random.randint(0,60*60*24)
    time.sleep(randelay)

    title = os.path.splitext(infileName)[0]
    #pub.tweet(outfilePath, title)


except Exception as e:
    print(e)

# sync to cloud: todo, done, out

