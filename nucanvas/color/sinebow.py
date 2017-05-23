# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
import math
from math import sin, pi
import colorsys

def sinebow(hue):
  '''Adapted from http://basecase.org/env/on-rainbows'''
  hue = -(hue + 0.5) # Start at red rotating clockwise
  rgb = sin(pi * hue), sin(pi * (hue + 1.0/3.0)), sin(pi * (hue + 2.0/3.0))
  return tuple(int(255  * c**2) for c in rgb)
 
def distinct_color_sequence(hue=0.0):
  # Hue is normalized from 0-1.0 for one revolution
  
  phi = (1 + 5**0.5) / 2
  golden_angle = phi #1.0 / phi**2
  
  #print('# GA:', math.degrees(golden_angle), phi)
  
  while(True):
    yield sinebow(hue)
    hue += golden_angle
    
def lighten(rgb, p):
  h,l,s = colorsys.rgb_to_hls(*(c / 255.0 for c in rgb))
  
  l = p + l - p*l
  return tuple(int(c * 255) for c in colorsys.hls_to_rgb(h,l,s))
    

if __name__ == '__main__': 

  import PIL
  from PIL import Image, ImageDraw

  cs = distinct_color_sequence()
  
  im = Image.new('RGB',(1024,10))
  d = ImageDraw.Draw(im)
  
  for i in range(256):
    hue = i / 256
    #r,g,b = sinebow(hue)
    r,g,b = next(cs)
    d.line([(i*4,0), (i*4,9)], (r,g,b), width=4)

  im.save('sinebow_rand.png')


  im = Image.new('RGB',(256,10))
  d = ImageDraw.Draw(im)
  
  for i in range(256):
    hue = i / 256
    r,g,b = sinebow(hue)
    d.line([(i,0), (i,9)], (r,g,b))

  im.save('sinebow.png')

