# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
from __future__ import print_function

import os
import math


def rounded_corner(start, apex, end, rad):

  # Translate all points with apex at origin
  start = (start[0] - apex[0], start[1] - apex[1])
  end = (end[0] - apex[0], end[1] - apex[1])
  
  # Get angles of each line segment
  enter_a = math.atan2(start[1], start[0]) % math.radians(360)
  leave_a = math.atan2(end[1], end[0]) % math.radians(360)
  
  #print('## enter, leave', math.degrees(enter_a), math.degrees(leave_a))
  
  # Determine bisector angle
  ea2 = abs(enter_a - leave_a)
  if ea2 > math.radians(180):
    ea2 = math.radians(360) - ea2
  bisect = ea2 / 2.0
  
  if bisect > math.radians(82): # Nearly colinear: Skip radius
    return (apex, apex, apex, -1)
  
  q = rad * math.sin(math.radians(90) - bisect) / math.sin(bisect)
  
  # Check that q is no more than half the shortest leg
  enter_leg = math.sqrt(start[0]**2 + start[1]**2)
  leave_leg = math.sqrt(end[0]**2 + end[1]**2)
  short_leg = min(enter_leg, leave_leg)
  if q > short_leg / 2:
    q = short_leg / 2
    # Compute new radius
    rad = q * math.sin(bisect) / math.sin(math.radians(90) - bisect)
    
  h = math.sqrt(q**2 + rad**2)
  
  # Center of circle

  # Determine which direction is the smallest angle to the leave point
  # Determine direction of arc
  # Rotate whole system so that enter_a is on x-axis
  delta = (leave_a - enter_a) % math.radians(360)
  if delta < math.radians(180): # CW
    bisect = enter_a + bisect
  else: # CCW
    bisect = enter_a - bisect

  #print('## Bisect2', math.degrees(bisect))
  center = (h * math.cos(bisect) + apex[0], h * math.sin(bisect) + apex[1])
  
  # Find start and end point of arcs
  start_p = (q * math.cos(enter_a) + apex[0], q * math.sin(enter_a) + apex[1])
  end_p = (q * math.cos(leave_a) + apex[0], q * math.sin(leave_a) + apex[1])
  
  return (center, start_p, end_p, rad)

def rotate_bbox(box, a):
  '''Rotate a bounding box 4-tuple by an angle in degrees'''
  corners = ( (box[0], box[1]), (box[0], box[3]), (box[2], box[3]), (box[2], box[1]) )
  a = -math.radians(a)
  sa = math.sin(a)
  ca = math.cos(a)
  
  rot = []
  for p in corners:
    rx = p[0]*ca + p[1]*sa
    ry = -p[0]*sa + p[1]*ca
    rot.append((rx,ry))
  
  # Find the extrema of the rotated points
  rot = list(zip(*rot))
  rx0 = min(rot[0])
  rx1 = max(rot[0])
  ry0 = min(rot[1])
  ry1 = max(rot[1])

  #print('## RBB:', box, rot)
    
  return (rx0, ry0, rx1, ry1)


class BaseSurface(object):
  def __init__(self, fname, def_styles, padding=0, scale=1.0):
    self.fname = fname
    self.def_styles = def_styles
    self.padding = padding
    self.scale = scale
    self.draw_bbox = False
    self.markers = {}
    
    self.shape_drawers = {}
    
  def add_shape_class(self, sclass, drawer):
    self.shape_drawers[sclass] = drawer
    
  def render(self, canvas, transparent=False):
    pass
    
  def text_bbox(self, text, font_params, spacing):
    pass

#################################
## NuCANVAS objects
#################################


class DrawStyle(object):
  def __init__(self):
    # Set defaults
    self.width = 1
    self.line_color = (0,0,255)
    self.line_cap = 'butt'
#    self.arrows = True
    self.fill = None
    self.text_color = (0,0,0)
    self.font = ('Helvetica', 12, 'normal')
    self.anchor = 'center'



class BaseShape(object):
  def __init__(self, options, **kwargs):
    self.options = {} if options is None else options
    self.options.update(kwargs)
    
    self._bbox = [0,0,1,1]
    self.tags = set()

  @property
  def points(self):
    return tuple(self._bbox)

  @property
  def bbox(self):
    if 'width' in self.options: # FIXME: rename to 'weight'
      w = self.options['width'] / 2.0
    else:
      w = 0

    x0 = min(self._bbox[0], self._bbox[2])
    x1 = max(self._bbox[0], self._bbox[2])
    y0 = min(self._bbox[1], self._bbox[3])
    y1 = max(self._bbox[1], self._bbox[3])
    
    x0 -= w
    x1 += w
    y0 -= w
    y1 += w

    return (x0,y0,x1,y1)

  @property
  def width(self):
    x0, _, x1, _ = self.bbox
    return x1 - x0

  @property
  def height(self):
    _, y0, _, y1 = self.bbox
    return y1 - y0

  @property
  def size(self):
    x0, y1, x1, y1 = self.bbox
    return (x1-x0, y1-y0)


  def param(self, name, def_styles=None):
    if name in self.options:
      return self.options[name]
    elif def_styles is not None:
      return getattr(def_styles, name)
    else:
      return None


  def is_tagged(self, item):
    return item in self.tags

  def update_tags(self):
    if 'tags' in self.options:
      self.tags = self.tags.union(self.options['tags'])
      del self.options['tags']

  def move(self, dx, dy):
    if self._bbox is not None:
      self._bbox[0] += dx
      self._bbox[1] += dy
      self._bbox[2] += dx
      self._bbox[3] += dy

  def dtag(self, tag=None):
    if tag is None:
      self.tags.clear()
    else:
      self.tags.discard(tag)

  def addtag(self, tag=None):
    if tag is not None:
      self.tags.add(tag)

  def draw(self, c):
    pass


class GroupShape(BaseShape):
  def __init__(self, surf, x0, y0, options, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._pos = (x0,y0)
    self._bbox = None
    self.shapes = []
    self.surf = surf # Needed for TextShape to get font metrics
    
    self.parent = None
    if 'parent' in options:
      self.parent = options['parent']
      del options['parent']
    
    self.update_tags()
    
  def ungroup(self):
    if self.parent is None:
      return
    
    x, y = self._pos
    for s in self.shapes:
      s.move(x, y)
      if isinstance(s, GroupShape):
        s.parent = self.parent

    # Transfer group children to our parent
    pshapes = self.parent.shapes
    pos = pshapes.index(self)

    # Remove this group
    self.parent.shapes = pshapes[:pos] + self.shapes + pshapes[pos+1:]
    
  def ungroup_all(self):
    for s in self.shapes:
      if isinstance(s, GroupShape):
        s.ungroup_all()
    self.ungroup()    
    
  def move(self, dx, dy):
    BaseShape.move(self, dx, dy)
    self._pos = (self._pos[0] + dx, self._pos[1] + dy)
    
  def create_shape(self, sclass, x0, y0, x1, y1, **options):
    shape = sclass(x0, y0, x1, y1, options)
    self.shapes.append(shape)
    self._bbox = None # Invalidate memoized box
    return shape

  def create_group(self, x0, y0, **options):
    options['parent'] = self
    shape = GroupShape(self.surf, x0, y0, options)
    self.shapes.append(shape)
    self._bbox = None # Invalidate memoized box
    return shape

  def create_group2(self, sclass, x0, y0, **options):
    options['parent'] = self
    shape = sclass(self.surf, x0, y0, options)
    self.shapes.append(shape)
    self._bbox = None # Invalidate memoized box
    return shape


  def create_arc(self, x0, y0, x1, y1, **options):
    return self.create_shape(ArcShape, x0, y0, x1, y1, **options)

  def create_line(self, x0, y0, x1, y1, **options):
    return self.create_shape(LineShape, x0, y0, x1, y1, **options)

  def create_oval(self, x0, y0, x1, y1, **options):
    return self.create_shape(OvalShape, x0, y0, x1, y1, **options)

  def create_rectangle(self, x0, y0, x1, y1, **options):
    return self.create_shape(RectShape, x0, y0, x1, y1, **options)

  def create_text(self, x0, y0, **options):
  
    # Must set default font now so we can use its metrics to get bounding box
    if 'font' not in options:
      options['font'] = self.surf.def_styles.font
  
    shape = TextShape(x0, y0, self.surf, options)
    self.shapes.append(shape)
    self._bbox = None # Invalidate memoized box

    # Add a unique tag to serve as an ID
    id_tag = 'id' + str(TextShape.next_text_id)
    shape.tags.add(id_tag)
    #return id_tag # FIXME
    return shape
    
  def create_path(self, nodes, **options):
    shape = PathShape(nodes, options)
    self.shapes.append(shape)
    self._bbox = None # Invalidate memoized box
    return shape

    
  @property
  def bbox(self):
    if self._bbox is None:
      bx0 = 0
      bx1 = 0
      by0 = 0
      by1 = 0

      boxes = [s.bbox for s in self.shapes]
      boxes = list(zip(*boxes))
      if len(boxes) > 0:
        bx0 = min(boxes[0])
        by0 = min(boxes[1])
        bx1 = max(boxes[2])
        by1 = max(boxes[3])
        
      if 'scale' in self.options:
        sx = sy = self.options['scale']
        bx0 *= sx
        by0 *= sy
        bx1 *= sx
        by1 *= sy
        
      if 'angle' in self.options:
        bx0, by0, bx1, by1 = rotate_bbox((bx0, by0, bx1, by1), self.options['angle'])

      tx, ty = self._pos
      self._bbox = [bx0+tx, by0+ty, bx1+tx, by1+ty]
      
    return self._bbox

  def dump_shapes(self, indent=0):
    print('{}{}'.format('  '*indent, repr(self)))

    indent += 1
    for s in self.shapes:
      if isinstance(s, GroupShape):
        s.dump_shapes(indent)
      else:
        print('{}{}'.format('  '*indent, repr(s)))

class LineShape(BaseShape):
  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._bbox = [x0, y0, x1, y1]
    self.update_tags()

class RectShape(BaseShape):
  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._bbox = [x0, y0, x1, y1]
    self.update_tags()


class OvalShape(BaseShape):
  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._bbox = [x0, y0, x1, y1]
    self.update_tags()

class ArcShape(BaseShape):
  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
    if 'closed' not in options:
      options['closed'] = False

    BaseShape.__init__(self, options, **kwargs)
    self._bbox = [x0, y0, x1, y1]
    self.update_tags()

  @property
  def bbox(self):
    lw = self.param('width')
    if lw is None:
      lw = 0
      
    lw /= 2.0

    # Calculate bounding box for arc segment
    x0, y0, x1, y1 = self.points
    xc = (x0 + x1) / 2.0
    yc = (y0 + y1) / 2.0
    hw = abs(x1 - x0) / 2.0
    hh = abs(y1 - y0) / 2.0

    start = self.options['start'] % 360
    extent = self.options['extent']
    stop = (start + extent) % 360

    if extent < 0:
      start, stop = stop, start  # Swap points so we can rotate CCW

    if stop < start:
      stop += 360 # Make stop greater than start

    angles = [start, stop]

    # Find the extrema of the circle included in the arc
    ortho = (start // 90) * 90 + 90
    while ortho < stop:
      angles.append(ortho)
      ortho += 90 # Rotate CCW


    # Convert all extrema points to cartesian
    points = [(hw * math.cos(math.radians(a)), -hh * math.sin(math.radians(a))) for a in angles]

    points = list(zip(*points))
    x0 = min(points[0]) + xc - lw
    y0 = min(points[1]) + yc - lw
    x1 = max(points[0]) + xc + lw
    y1 = max(points[1]) + yc + lw

    if 'width' in self.options:
      w = self.options['width'] / 2.0
      # FIXME: This doesn't properly compensate for the true extrema of the stroked outline
      x0 -= w
      x1 += w
      y0 -= w
      y1 += w

    #print('@@ ARC BB:', (bx0,by0,bx1,by1), hw, hh, angles, start, extent)
    return (x0,y0,x1,y1)

class PathShape(BaseShape):
  def __init__(self, nodes, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self.nodes = nodes
    self.update_tags()

  @property
  def bbox(self):
    extrema = []
    for p in self.nodes:
      if len(p) == 2:
        extrema.append(p)
      elif len(p) == 6: # FIXME: Compute tighter extrema of spline
        extrema.append(p[0:2])
        extrema.append(p[2:4])
        extrema.append(p[4:6])
      elif len(p) == 5: # Arc
        extrema.append(p[0:2])
        extrema.append(p[2:4])
        
    extrema = list(zip(*extrema))
    x0 = min(extrema[0])
    y0 = min(extrema[1])
    x1 = max(extrema[0])
    y1 = max(extrema[1])

    if 'width' in self.options:
      w = self.options['width'] / 2.0
      # FIXME: This doesn't properly compensate for the true extrema of the stroked outline
      x0 -= w
      x1 += w
      y0 -= w
      y1 += w

    return (x0, y0, x1, y1)



class TextShape(BaseShape):
  text_id = 1
  def __init__(self, x0, y0, surf, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._pos = (x0, y0)

    if 'spacing' not in options:
      options['spacing'] = -8
    if 'anchor' not in options:
      options['anchor'] = 'c'
      
    spacing = options['spacing']

    bx0,by0, bx1,by1, baseline = surf.text_bbox(options['text'], options['font'], spacing)
    w = bx1 - bx0
    h = by1 - by0
    
    self._baseline = baseline
    self._bbox = [x0, y0, x0+w, y0+h]
    self._anchor_off = self.anchor_offset
    
    self.update_tags()

  @property
  def bbox(self):
    x0, y0, x1, y1 = self._bbox
    ax, ay = self._anchor_off
    return (x0+ax, y0+ay, x1+ax, y1+ay)

  @property
  def anchor_decode(self):
    anchor = self.param('anchor').lower()

    anchor = anchor.replace('center','c')
    anchor = anchor.replace('east','e')
    anchor = anchor.replace('west','w')

    if 'e' in anchor:
      anchorh = 'e'
    elif 'w' in anchor:
      anchorh = 'w'
    else:
      anchorh = 'c'

    if 'n' in anchor:
      anchorv = 'n'
    elif 's' in anchor:
      anchorv = 's'
    else:
      anchorv = 'c'

    return (anchorh, anchorv)

  @property
  def anchor_offset(self):
    x0, y0, x1, y1 = self._bbox
    w = abs(x1 - x0)
    h = abs(y1 - y0)
    hw = w / 2.0
    hh = h / 2.0

    spacing = self.param('spacing')

    anchorh, anchorv = self.anchor_decode
    ax = 0
    ay = 0
    
    if 'n' in anchorv:
      ay = hh + (spacing // 2)
    elif 's' in anchorv:
      ay = -hh - (spacing // 2)
    
    if 'e' in anchorh:
      ax = -hw
    elif 'w' in anchorh:
      ax = hw
      
    # Convert from center to upper-left corner
    return (ax - hw, ay - hh)

  @property
  def next_text_id(self):
    rval = TextShape.text_id
    TextShape.text_id += 1
    return rval



class DoubleRectShape(BaseShape):
  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
    BaseShape.__init__(self, options, **kwargs)
    self._bbox = [x0, y0, x1, y1]
    self.update_tags()

def cairo_draw_DoubleRectShape(shape, surf):
  c = surf.ctx
  x0, y0, x1, y1 = shape.points
  
  c.rectangle(x0,y0, x1-x0,y1-y0)

  stroke = True if shape.options['width'] > 0 else False

  if 'fill' in shape.options:
    c.set_source_rgba(*rgb_to_cairo(shape.options['fill']))
    if stroke:
      c.fill_preserve()
    else:
      c.fill()

  if stroke:
    # FIXME c.set_source_rgba(*default_pen)
    c.set_source_rgba(*rgb_to_cairo((100,200,100)))
    c.stroke()

    c.rectangle(x0+4,y0+4, x1-x0-8,y1-y0-8)
    c.stroke()

