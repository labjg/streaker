#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Lines In Space (LIS) streaker
# Smear images horizontally or vertically.
# By James Gilbert (@labjg); feel free to take, use, fix, hack etc.

from PIL import Image, ImageEnhance
from PIL.ExifTags import TAGS
import numpy as np


def streak(infile, outfile, vertical=False, rMedian=0, contrast=1.0,
           saturation=1.0, sharpness=1.0, verbose=False):
    """ Add docstrig here. Contrast=1.5 is good??
    """
    im = Image.open(infile)

    # First thing is to deal with EXIF orientation flag headaches:
    if verbose: print("Reading EXIF tags...")
    try:
        tagList = {}
        info = im._getexif()
        for tag, val in info.items():
            decoded = TAGS.get(tag,tag)
            tagList[decoded] = val

        if verbose: print("EXIF orientation tag is", tagList['Orientation'])
        if tagList['Orientation'] == 3:
            if verbose: print("Rotating 180 degs...")
            im = im.transpose(Image.ROTATE_180)
        elif tagList['Orientation'] == 6:
            if verbose: print("Rotating 90 degs...")
            im = im.transpose(Image.ROTATE_270)
        elif tagList['Orientation'] == 8:
            if verbose: print("Rotating 270 degs...")
            im = im.transpose(Image.ROTATE_90)
    except Exception as e:
        if verbose: print(e)

    # Now for the actual processing:
    imArr = np.array(im)

    if not vertical:
        if verbose: print("Calculating pixel values for horizontal smear...")
        # A single column of pixel values - will be 'wiped' sideways later:
        pxVals = np.zeros((imArr.shape[0],imArr.shape[2]))
        # Calculate the average pixel value of every row:
        for y in range(pxVals.shape[0]):
            pxVals[y,:] = np.mean(imArr[y,:], axis=0)
    else:
        if verbose: print("Calculating pixel values for vertical smear...")
        # A single row of pixel values - will be 'wiped' downwards later:
        pxVals = np.zeros((imArr.shape[1],imArr.shape[2]))
        # Calculate the average pixel value of every column:
        for x in range(pxVals.shape[0]):
            pxVals[x,:] = np.mean(imArr[:,x], axis=0)

    # Apply a median filter if specified:
    if rMedian > 0:
        if verbose: print("Applying median filter...")
        # Check the median mask isn't too big for the image:
        if rMedian > (pxVals.shape[0]-1):
            if verbose: print("Median mask size reduced from %i to %i"\
                              % (rMedian, pxVals.shape[0]-1))
            rMedian = pxVals.shape[0] - 1
        # Create a padded array, mirroring the px values:
        size_pad = (pxVals.shape[0]+(2*rMedian), pxVals.shape[1])
        pxVals_pad = np.zeros(size_pad)
        pxVals_pad[rMedian:size_pad[0]-rMedian] = pxVals
        for r in range(rMedian):
            pxVals_pad[r] = pxVals[rMedian-r]
            pxVals_pad[size_pad[0]-1-r] = pxVals[pxVals.shape[0]-1-rMedian+r]
        # Calculate the median values:
        for i in range(pxVals.shape[0]):
            pxVals[i,:] = np.median(pxVals_pad[i:i+(2*rMedian)+1,:], axis=0)
        
    # 'Wipe' the pixel values across the whole image:
    if verbose: print("Smearing image...")
    if not vertical:
        for y in range(pxVals.shape[0]):
            imArr[y,:] = pxVals[y]
    else:
        for x in range(pxVals.shape[0]):
            imArr[:,x] = pxVals[x]

    im = Image.fromarray(imArr)

    # Adjust contrast if required:
    if contrast > 1.0:
        if verbose: print("Adjusting contrast...")
        enh = ImageEnhance.Contrast(im)
        im = enh.enhance(contrast)

    # Adjust saturation if required:
    if saturation > 1.0:
        if verbose: print("Adjusting saturation...")
        enh = ImageEnhance.Color(im)
        im = enh.enhance(saturation)

    # Adjust sharpness if required:
    if sharpness > 1.0:
        if verbose: print("Adjusting sharpness...")
        enh = ImageEnhance.Sharpness(im)
        im = enh.enhance(sharpness)
    
    # Finaly, save the processed image:
    if verbose: print("Saving output image...")
    im.save(outfile)
