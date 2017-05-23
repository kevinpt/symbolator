# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
from __future__ import print_function

import os
import math

import cairo
from shapes import *

try:
  import pango
  import pangocairo
  use_pygobject = False
except ImportError:
  from gi.repository import Pango as pango
  from gi.repository import PangoCairo as pangocairo
  use_pygobject = True

#################################
## CAIRO objects
#################################

def rgb_to_cairo(rgb):
  if len(rgb) == 4:
    r,g,b,a = rgb
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)

  else:
    r,g,b = rgb
    return (r / 255.0, g / 255.0, b / 255.0, 1.0)

def cairo_font(tk_font):
  family, size, weight = tk_font
  return pango.FontDescription('{} {} {}'.format(family, weight, size))


def cairo_line_cap(line_cap):
  if line_cap == 'round':
    return cairo.LINE_CAP_ROUND
  elif line_cap == 'square':
    return cairo.LINE_CAP_SQUARE
  else:
    return cairo.LINE_CAP_BUTT

    
class CairoSurface(BaseSurface):
  def __init__(self, fname, def_styles, padding=0, scale=1.0):
    BaseSurface.__init__(self, fname, def_styles, padding, scale)
    self.ctx = None
    
  def render(self, canvas, transparent=False):
  
    x0,y0,x1,y1 = canvas.bbox('all')
    self.markers = canvas.markers
    
    W = int((x1 - x0 + 2*self.padding) * self.scale)
    H = int((y1 - y0 + 2*self.padding) * self.scale)
  
    ext = os.path.splitext(self.fname)[1].lower()

    if ext == '.svg':
      surf = cairo.SVGSurface(self.fname, W, H)
    elif ext == '.pdf':
      surf = cairo.PDFSurface(self.fname, W, H)
    elif ext in ('.ps', '.eps'):
      surf = cairo.PSSurface(self.fname, W, H)
      if ext == '.eps':
        surf.set_eps(True)
    else: # Bitmap
      surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)

    self.ctx = cairo.Context(surf)
    ctx = self.ctx

    if not transparent:
      # Fill background
      ctx.rectangle(0,0, W,H)
      ctx.set_source_rgba(1.0,1.0,1.0)
      ctx.fill()

    ctx.scale(self.scale, self.scale)
    ctx.translate(-x0 + self.padding, -y0 + self.padding)

    if self.draw_bbox:
      last = len(canvas.shapes)
      for s in canvas.shapes[:last]:
        bbox = s.bbox
        r = canvas.create_rectangle(*bbox, line_color=(255,0,0, 127), fill=(0,255,0,90))

    for s in canvas.shapes:
      self.draw_shape(s)


    if ext in ('.svg', '.pdf', '.ps', '.eps'):
      surf.show_page()
    else:
      surf.write_to_png(self.fname)

  def text_bbox(self, text, font_params, spacing=0):
    return CairoSurface.cairo_text_bbox(text, font_params, spacing, self.scale)

  @staticmethod
  def cairo_text_bbox(text, font_params, spacing=0, scale=1.0):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
    ctx = cairo.Context(surf)

    # The scaling must match the final context.
    # If not there can be a mismatch between the computed extents here
    # and those generated for the final render.
    ctx.scale(scale, scale)
    
    font = cairo_font(font_params)


    if use_pygobject:
      status, attrs, plain_text, _ = pango.parse_markup(text, len(text), '\0')
      
      layout = pangocairo.create_layout(ctx)
      pctx = layout.get_context()
      fo = cairo.FontOptions()
      fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
      pangocairo.context_set_font_options(pctx, fo)
      layout.set_font_description(font)
      layout.set_spacing(spacing * pango.SCALE)
      layout.set_text(plain_text, len(plain_text))
      layout.set_attributes(attrs)

      li = layout.get_iter() # Get first line of text
      baseline = li.get_baseline() / pango.SCALE

      re = layout.get_pixel_extents()[1] # Get logical extents
      extents = (re.x, re.y, re.x + re.width, re.y + re.height)

    else: # pyGtk
      attrs, plain_text, _ = pango.parse_markup(text)

      pctx = pangocairo.CairoContext(ctx)
      pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
      layout = pctx.create_layout()
      layout.set_font_description(font)
      layout.set_spacing(spacing * pango.SCALE)
      layout.set_text(plain_text)
      layout.set_attributes(attrs)

      li = layout.get_iter() # Get first line of text
      baseline = li.get_baseline() / pango.SCALE

      #print('@@ EXTENTS:', layout.get_pixel_extents()[1], spacing)
      extents = layout.get_pixel_extents()[1] # Get logical extents

    return [extents[0], extents[1], extents[2], extents[3], baseline]



  @staticmethod
  def draw_text(x, y, text, font, text_color, spacing, c):
    c.save()
    c.set_source_rgba(*rgb_to_cairo(text_color))
    font = cairo_font(font)

    c.translate(x, y)
    
    if use_pygobject:
      status, attrs, plain_text, _ = pango.parse_markup(text, len(text), '\0')
      
      layout = pangocairo.create_layout(c)
      pctx = layout.get_context()
      fo = cairo.FontOptions()
      fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
      pangocairo.context_set_font_options(pctx, fo)
      layout.set_font_description(font)
      layout.set_spacing(spacing * pango.SCALE)
      layout.set_text(plain_text, len(plain_text))
      layout.set_attributes(attrs)
      pangocairo.update_layout(c, layout)
      pangocairo.show_layout(c, layout)

    else: # pyGtk
      attrs, plain_text, _ = pango.parse_markup(text)
      
      pctx = pangocairo.CairoContext(c)
      pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
      layout = pctx.create_layout()
      layout.set_font_description(font)
      layout.set_spacing(spacing * pango.SCALE)
      layout.set_text(plain_text)
      layout.set_attributes(attrs)
      pctx.update_layout(layout)
      pctx.show_layout(layout)
      
    c.restore()

  def draw_marker(self, name, mp, tp, width, c):
    if name in self.markers:
      m_shape, ref, orient, units = self.markers[name]

      c.save()
      c.translate(*mp)
      if orient == 'auto':
        angle = math.atan2(tp[1]-mp[1], tp[0]-mp[0])
        c.rotate(angle)
      elif isinstance(orient, int):
        angle = math.radians(orient)
        c.rotate(angle)

      if units == 'stroke':
        c.scale(width,width)
        
      c.translate(-ref[0], -ref[1])
      
      self.draw_shape(m_shape)
      c.restore()
    
  def draw_shape(self, shape):
    c = self.ctx
    default_pen = rgb_to_cairo(self.def_styles.line_color)
    c.set_source_rgba(*default_pen)

    width = shape.param('width', self.def_styles)
    fill = shape.param('fill', self.def_styles)
    line_color = shape.param('line_color', self.def_styles)
    line_cap = cairo_line_cap(shape.param('line_cap', self.def_styles))
    
    stroke = True if width > 0 else False

    c.set_line_width(width)
    c.set_line_cap(line_cap)

    if shape.__class__ in self.shape_drawers:
      self.shape_drawers[shape.__class__](shape, self)
    
    elif isinstance(shape, GroupShape):
      c.save()
      c.translate(*shape._pos)
      if 'scale' in shape.options:
        c.scale(shape.options['scale'], shape.options['scale'])
      if 'angle' in shape.options:
        c.rotate(math.radians(shape.options['angle']))

      for s in shape.shapes:
        self.draw_shape(s)
      c.restore()

    elif isinstance(shape, TextShape):
      x0, y0, x1, y1 = shape.bbox
      
      text = shape.param('text', self.def_styles)      
      font = shape.param('font', self.def_styles)
      text_color = shape.param('text_color', self.def_styles)
      anchor = shape.param('anchor', self.def_styles).lower()
      spacing = shape.param('spacing', self.def_styles)
      
      CairoSurface.draw_text(x0, y0, text, font, text_color, spacing, c)
      

    elif isinstance(shape, LineShape):
      x0, y0, x1, y1 = shape.points
      
      marker = shape.param('marker')
      marker_start = shape.param('marker_start')
      marker_mid = shape.param('marker_mid')
      marker_end = shape.param('marker_end')
      if marker is not None:
        if marker_start is None:
          marker_start = marker
        if marker_end is None:
          marker_end = marker
        if marker_mid is None:
          marker_mid = marker
          
      adjust = shape.param('marker_adjust')
      if adjust is None:
        adjust = 0
        
      if adjust > 0:
        angle = math.atan2(y1-y0, x1-x0)
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        if marker_start in self.markers:
          # Get bbox of marker
          m_shape, ref, orient, units = self.markers[marker_start]
          mx0, my0, mx1, my1 = m_shape.bbox
          soff = (ref[0] - mx0) * adjust
          
          # Move start point
          x0 += soff * dx
          y0 += soff * dy

        if marker_end in self.markers:
          # Get bbox of marker
          m_shape, ref, orient, units = self.markers[marker_end]
          mx0, my0, mx1, my1 = m_shape.bbox
          eoff = (mx1 - ref[0]) * adjust
          
          # Move end point
          x1 -= eoff * dx
          y1 -= eoff * dy


      c.move_to(x0,y0)
      c.line_to(x1,y1)
      c.stroke()

      # Draw any markers

      self.draw_marker(marker_start, (x0,y0), (x1,y1), width, c)
      self.draw_marker(marker_end, (x1,y1), (x1 + 2*(x1-x0),y1 + 2*(y1-y0)), width,  c)
      self.draw_marker(marker_mid, ((x0 + x1)/2,(y0+y1)/2), (x1,y1), width, c)


    elif isinstance(shape, RectShape):
      x0, y0, x1, y1 = shape.points
      c.rectangle(x0,y0, x1-x0,y1-y0)

      if fill is not None:
        c.set_source_rgba(*rgb_to_cairo(fill))
        if stroke:
          c.fill_preserve()
        else:
          c.fill()

      if stroke:
        c.set_source_rgba(*rgb_to_cairo(line_color))
        c.stroke()


    elif isinstance(shape, OvalShape):
      x0, y0, x1, y1 = shape.points
      xc = (x0 + x1) / 2.0
      yc = (y0 + y1) / 2.0
      w = abs(x1 - x0)
      h = abs(y1 - y0)
      
      c.save()
      # Set transformation matrix to permit drawing ovals
      c.translate(xc,yc)
      c.scale(w/2.0, h/2.0)
      c.arc(0,0, 1, 0, 2 * math.pi)
      #c.arc(xc,yc, rad, 0, 2 * math.pi)
      
      if fill is not None:
        c.set_source_rgba(*rgb_to_cairo(fill))
        if stroke:
          c.fill_preserve()
        else:
          c.fill()

      c.restore() # Stroke with original transform

      if stroke:
        c.set_source_rgba(*rgb_to_cairo(line_color))
        c.stroke()



    elif isinstance(shape, ArcShape):
      x0, y0, x1, y1 = shape.points
      xc = (x0 + x1) / 2.0
      yc = (y0 + y1) / 2.0
      w = abs(x1 - x0)
      h = abs(y1 - y0)

      start = shape.options['start']
      extent = shape.options['extent']

      # Start and end angles
      sa = -math.radians(start)
      ea = -math.radians(start + extent)

      # Tk has opposite angle convention from Cairo
      #   Positive extent is a negative rotation in Cairo
      #   Negative extent is a positive rotation in Cairo
      
      c.save()
      
      c.translate(xc, yc)
      c.scale(w/2.0, h/2.0)
        
      if fill is not None:
        c.move_to(0,0)
        if extent >= 0:
          c.arc_negative(0,0, 1.0, sa, ea)
        else:
          c.arc(0,0, 1.0, sa, ea)
        c.set_source_rgba(*rgb_to_cairo(fill))
        c.fill()
        

      # Stroke arc segment
      c.new_sub_path()
      if extent >= 0:
        c.arc_negative(0,0, 1.0, sa, ea)
      else:
        c.arc(0,0, 1.0, sa, ea)

      c.restore()
      c.set_source_rgba(*rgb_to_cairo(line_color))
      c.stroke()

        
    elif isinstance(shape, PathShape):
    
      pp = shape.nodes[0]

      for n in shape.nodes:
        if n == 'z':
          c.close_path()
          break
        elif len(n) == 2:
          c.line_to(*n)
          pp = n
        elif len(n) == 6:
          c.curve_to(*n)
          pp = n[4:6]
        elif len(n) == 5: # Arc (javascript arcto() args)
          #print('# arc:', pp)
          #pp = self.draw_rounded_corner(pp, n[0:2], n[2:4], n[4], c)

          center, start_p, end_p, rad = rounded_corner(pp, n[0:2], n[2:4], n[4])
          if rad < 0: # No arc
            c.line_to(*end_p)
          else:
            # Determine angles to arc end points
            ostart_p = (start_p[0] - center[0], start_p[1] - center[1])
            oend_p = (end_p[0] - center[0], end_p[1] - center[1])
            start_a = math.atan2(ostart_p[1], ostart_p[0]) % math.radians(360)
            end_a = math.atan2(oend_p[1], oend_p[0]) % math.radians(360)

            # Determine direction of arc
            # Rotate whole system so that start_a is on x-axis
            # Then if delta < 180 cw  if delta > 180 ccw
            delta = (end_a - start_a) % math.radians(360)

            #print('# start_a, end_a', math.degrees(start_a), math.degrees(end_a),
            #            math.degrees(delta))

            if delta < math.radians(180): # CW
              c.arc(center[0],center[1], rad, start_a, end_a)
            else: # CCW
              c.arc_negative(center[0],center[1], rad, start_a, end_a)
          pp = end_p

          #print('# pp:', pp)


      if fill is not None:
        c.set_source_rgba(*rgb_to_cairo(fill))
        if stroke:
          c.fill_preserve()
        else:
          c.fill()

      if stroke:
        c.set_source_rgba(*rgb_to_cairo(line_color))
        c.stroke()

