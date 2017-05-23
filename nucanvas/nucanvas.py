# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
from __future__ import print_function

from shapes import GroupShape, DrawStyle


class NuCanvas(GroupShape):
  '''This is a clone of the Tk canvas subset used by the original Tcl
     It implements an abstracted canvas that can render objects to different
     backends other than just a Tk canvas widget.
  '''
  def __init__(self, surf):
    GroupShape.__init__(self, surf, 0, 0, {})
    self.markers = {}
    
  def set_surface(self, surf):
    self.surf = surf
    
  def clear_shapes(self):
    self.shapes = []
    
  def _get_shapes(self, item=None):
    # Filter shapes
    if item is None or item == 'all':
      shapes = self.shapes
    else:
      shapes = [s for s in self.shapes if s.is_tagged(item)]
    return shapes


  def render(self):
    self.surf.render(self)
    
  def add_marker(self, name, shape, ref=(0,0), orient='auto', units='stroke'):
    self.markers[name] = (shape, ref, orient, units)

  def bbox(self, item=None):
    bx0 = 0
    bx1 = 0
    by0 = 0
    by1 = 0

    boxes = [s.bbox for s in self._get_shapes(item)]
    boxes = list(zip(*boxes))
    if len(boxes) > 0:
      bx0 = min(boxes[0])
      by0 = min(boxes[1])
      bx1 = max(boxes[2])
      by1 = max(boxes[3])

    return [bx0, by0, bx1, by1]

  def move(self, item, dx, dy):
    for s in self._get_shapes(item):
      s.move(dx, dy)

  def tag_raise(self, item):
    to_raise = self._get_shapes(item)
    for s in to_raise:
      self.shapes.remove(s)
    self.shapes.extend(to_raise)

  def addtag_withtag(self, tag, item):
    for s in self._get_shapes(item):
      s.addtag(tag)


  def dtag(self, item, tag=None):
    for s in self._get_shapes(item):
      s.dtag(tag)

  def draw(self, c):
    '''Draw all shapes on the canvas'''
    for s in self.shapes:
      tk_draw_shape(s, c)

  def delete(self, item):
    for s in self._get_shapes(item):
      self.shapes.remove(s)


if __name__ == '__main__':

  from svg_backend import SvgSurface
  from cairo_backend import CairoSurface
  from shapes import PathShape

  #surf = CairoSurface('nc.png', DrawStyle(), padding=5, scale=2)
  surf = SvgSurface('nc.svg', DrawStyle(), padding=5, scale=2)
  
  #surf.add_shape_class(DoubleRectShape, cairo_draw_DoubleRectShape)
  
  nc = NuCanvas(surf)
  

  nc.add_marker('arrow_fwd',
    PathShape(((0,-4), (2,-1, 2,1, 0,4), (8,0), 'z'), fill=(0,0,0, 120), width=0),
    (3.2,0), 'auto')

  nc.add_marker('arrow_back',
    PathShape(((0,-4), (-2,-1, -2,1, 0,4), (-8,0), 'z'), fill=(0,0,0, 120), width=0),
    (-3.2,0), 'auto')

#
#  nc.create_rectangle(5,5, 20,20, fill=(255,0,0,127))
#  nc.create_rectangle(35,2, 40,60, width=2, fill=(255,0,0))
#
#  nc.create_rectangle(65,35, 150,50, width=0, fill=(255,0,0))
#  nc.create_oval(65,35, 150,50, width=2, fill=(0,100,255))
##
##  nc.create_shape(DoubleRectShape, 10,80, 40,140, width=3, fill=(0,255,255))
#  g = nc.create_group(30,20, angle=-30, scale=2)
#  g.create_rectangle(0,0,40,40, fill=(100,100,200, 150), width=3, line_color=(0,0,0))
#  g.create_rectangle(0,50,40,70, fill=(100,200,100), width=3)
#
#  gbb = g.bbox
#  nc.create_rectangle(*gbb, width=1)

#  abox = (60,60, 120,100)
#  nc.create_rectangle(*abox, line_color=(10,255,10), width=4)
#  arc = nc.create_arc(*abox, start=-45, extent=170, width=4, line_color=(255,0,0), fill=(0,255,0,127))
#  abb = arc.bbox
#  nc.create_rectangle(*abb, width=1)
#  
#  nc.create_path([(14,14), (30,4), (150,-60, 190,110, 140,110), (20,120), 'z'], fill=(255,100,0,127), width=2)
#
#  nc.create_path([(20,40), (30,70), (40,120, 60,50, 10), (60, 50, 80,90, 10), (80, 90, 150,89, 15),
#       (150, 89), (130,20), 'z'], width=1)

  nc.create_line(30,50, 200,100, width=5, line_color=(200,100,50,100), marker_start='arrow_back',
    marker_end='arrow_fwd')


  nc.create_rectangle(30,85, 60,105, width=1, line_color=(255,0,0))
  nc.create_line(30,90, 60,90, width=2, marker_start='arrow_back',
    marker_end='arrow_fwd')

  nc.create_line(30,100, 60,100, width=2, marker_start='arrow_back',
    marker_end='arrow_fwd', marker_adjust=1.0)


#        ls.options['marker_start'] = 'arrow_back'
#      ls.options['marker_end'] = 'arrow_fwd'
#      ls.options['marker_adjust'] = 0.8

  nc.create_oval(50-2,80-2, 50+2,80+2, width=0, fill=(255,0,0))
  nc.create_text(50,80, text='Hello world', anchor='nw', font=('Helvetica', 14, 'normal'), text_color=(0,0,0), spacing=-8)
  
  nc.create_oval(50-2,100-2, 50+2,100+2, width=0, fill=(255,0,0))
  nc.create_text(50,100, text='Hello world', anchor='ne')

  surf.draw_bbox = True
  nc.render()
  
