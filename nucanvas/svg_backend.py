from __future__ import print_function

import io
import os
import math

#import cairo
from shapes import *

#try:
#  import pango
#  import pangocairo
#  use_pygobject = False
#except ImportError:
#  from gi.repository import Pango as pango
#  from gi.repository import PangoCairo as pangocairo
#  use_pygobject = True

#################################
## SVG objects
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


def rgb_to_hex(rgb):
  return '#{:02X}{:02X}{:02X}'.format(*rgb[:3])

def hex_to_rgb(hex_color):
  v = int(hex_color[1:], 16)
  b = v & 0xFF
  g = (v >> 8) & 0xFF
  r = (v >> 16) & 0xFF
  return (r,g,b)

    
class SvgSurface(BaseSurface):
  def __init__(self, fname, def_styles, padding=0, scale=1.0):
    BaseSurface.__init__(self, fname, def_styles, padding, scale)
    
    self.fh = None
    
  svg_header = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created by Syntax-Trax http://kevinpt.github.io/syntax-trax -->
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xml:space="preserve"
width="{}" height="{}" version="1.1">
<style type="text/css">
<![CDATA[
{}
.label {{fill:#000;
  text-anchor:middle;
  font-size:16pt; font-weight:bold; font-family:Sans;}}
.link {{fill: #0D47A1;}}
.link:hover {{fill: #0D47A1; text-decoration:underline;}}
.link:visited {{fill: #4A148C;}}
]]>
</style>
<defs>
  <marker id="arrow" markerWidth="5" markerHeight="4" refX="2.5" refY="2" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0.5,2 L0,4 L4.5,2 z" fill="{}" />
  </marker>
</defs>
'''

  def render(self, canvas, transparent=False):
    x0,y0,x1,y1 = canvas.bbox('all')
    self.markers = canvas.markers
    
    W = int((x1 - x0 + 2*self.padding) * self.scale)
    H = int((y1 - y0 + 2*self.padding) * self.scale)
    
    x0 = int(x0)
    y0 = int(y0)
    
    #print('###', x0, y0)

    # Reposition all shapes in the viewport
    for s in canvas.shapes:
      s.move(-x0 + self.padding, -y0 + self.padding)

    # Generate CSS for fonts
    text_color = rgb_to_hex(self.def_styles.text_color)
    css = []

    fonts = {}
    # Collect fonts from common styles
    for f in [k for k in dir(self.def_styles) if k.endswith('_font')]:
      fonts[f] = (getattr(self.def_styles, f), text_color)
#    # Collect node style fonts
#    for ns in styles.node_styles:
#      fonts[ns.name + '_font'] = (ns.font, rgb_to_hex(ns.text_color))

    for f, fs in fonts.iteritems():
      family, size, weight = fs[0]
      text_color = fs[1]

      if weight == 'italic':
        style = 'italic'
        weight = 'normal'
      else:
        style = 'normal'

      css.append('''.{} {{fill:{}; text-anchor:middle;
    font-family:{}; font-size:{}pt; font-weight:{}; font-style:{};}}'''.format(f,
      text_color, family, size, weight, style))


    font_styles = '\n'.join(css)
    line_color = rgb_to_hex(self.def_styles.line_color)

    with io.open(self.fname, 'w', encoding='utf-8') as fh:
      self.fh = fh
      fh.write(SvgSurface.svg_header.format(W,H, font_styles, line_color))
      if not transparent:
        fh.write(u'<rect width="100%" height="100%" fill="white"/>')
      for s in canvas.shapes:
        self.draw_shape(s)
      fh.write(u'</svg>')


  def text_bbox(self, text, font_params, spacing = 0):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
    ctx = cairo.Context(surf)

    # The scaling must match the final context.
    # If not there can be a mismatch between the computed extents here
    # and those generated for the final render.
    ctx.scale(self.scale, self.scale)
    
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
      
      #print('@@ EXTENTS:', layout.get_pixel_extents()[1], spacing)
      extents = layout.get_pixel_extents()[1] # Get logical extents
    w = extents[2] - extents[0]
    h = extents[3] - extents[1]
    x0 = - w // 2.0
    y0 = - h // 2.0
    return [x0,y0, x0+w,y0+h]



  @staticmethod
  def draw_text(x, y, text, font, text_color, spacing, c):
    c.save()
    #print('## TEXT COLOR:', text_color)
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
      #print('# MARKER:', name)
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
        print('  SCALE:', width)
        c.scale(width,width)
        
      c.translate(-ref[0], -ref[1])
      
      
      self.draw_shape(m_shape)
      c.restore()
    
  def draw_shape(self, shape):
    fh = self.fh
    default_pen = rgb_to_hex(self.def_styles.line_color)
    #c.set_source_rgba(*default_pen)
    
    attrs = {
      'stroke': 'none',
      'fill': 'none'
    }

    width = shape.param('width', self.def_styles)
    fill = shape.param('fill', self.def_styles)
    line_color = shape.param('line_color', self.def_styles)
    #line_cap = cairo_line_cap(shape.param('line_cap', self.def_styles))
    
    stroke = True if width > 0 else False
    
    if width > 0:
      attrs['stroke-width'] = width

      if line_color is not None:
        attrs['stroke'] = rgb_to_hex(line_color)
        if len(line_color) == 4:
          attrs['stroke-opacity'] = line_color[3] / 255.0
      else:
        attrs['stroke'] = default_pen
      
      
    if fill is not None:
      attrs['fill'] = rgb_to_hex(fill)
      if len(fill) == 4:
        attrs['fill-opacity'] = fill[3] / 255.0

    #c.set_line_width(width)
    #c.set_line_cap(line_cap)

    # Draw custom shapes
    if shape.__class__ in self.shape_drawers:
      self.shape_drawers[shape.__class__](shape, self)
    
    # Draw standard shapes
    elif isinstance(shape, GroupShape):
      tform = [u'translate({},{})'.format(*shape._pos)]
      
      if 'scale' in shape.options:
        tform.append(u'scale({})'.format(shape.options['scale']))
      if 'angle' in shape.options:
        tform.append(u'rotate({})'.format(shape.options['angle']))

      fh.write(u'<g transform="{}">\n'.format(u' '.join(tform)))
      
      for s in shape.shapes:
        self.draw_shape(s)
      
      fh.write(u'</g>\n')

    elif isinstance(shape, TextShape):
      x0, y0, x1, y1 = shape.points
      
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
          #print("# SOFF", mx0, ref[0], soff)
          
          # Move start point
          x0 += soff * dx
          y0 += soff * dy

        if marker_end in self.markers:
          # Get bbox of marker
          m_shape, ref, orient, units = self.markers[marker_end]
          mx0, my0, mx1, my1 = m_shape.bbox
          eoff = (mx1 - ref[0]) * adjust
          #print("# EOFF", mx1, ref[0], eoff)
          
          # Move end point
          x1 -= eoff * dx
          y1 -= eoff * dy

      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])

      fh.write(u'<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x0,y0, x1,y1, attributes))
#      # Draw any markers
      # FIXME
#      self.draw_marker(marker_start, (x0,y0), (x1,y1), width, c)
#      self.draw_marker(marker_end, (x1,y1), (x1 + 2*(x1-x0),y1 + 2*(y1-y0)), width,  c)
#      self.draw_marker(marker_mid, ((x0 + x1)/2,(y0+y1)/2), (x1,y1), width, c)


    elif isinstance(shape, RectShape):
      x0, y0, x1, y1 = shape.points
      
      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])

      fh.write(u'<rect x="{}" y="{}" width="{}" height="{}" {}/>\n'.format(
        x0,y0, x1-x0, y1-y0, attributes))

    elif isinstance(shape, OvalShape):
      x0, y0, x1, y1 = shape.points
      xc = (x0 + x1) / 2.0
      yc = (y0 + y1) / 2.0
      w = abs(x1 - x0)
      h = abs(y1 - y0)
      rad = min(w,h)
      
      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])
      fh.write(u'<ellipse cx="{}" cy="{}" rx="{}" ry="{}" {}/>\n'.format(xc, yc,
              w/2.0, h/2.0, attributes))


    elif isinstance(shape, ArcShape):
      x0, y0, x1, y1 = shape.points
      xc = (x0 + x1) / 2.0
      yc = (y0 + y1) / 2.0
      #rad = abs(x1 - x0) / 2.0
      w = abs(x1 - x0)
      h = abs(y1 - y0)
      xr = w / 2.0
      yr = h / 2.0


      start = shape.options['start'] % 360
      extent = shape.options['extent']
      stop = (start + extent) % 360

      #print('## ARC:', start, extent, stop)

      # Start and end angles
      sa = math.radians(start)
      ea = math.radians(stop)

      xs = xc + xr * math.cos(sa)
      ys = yc - yr * math.sin(sa)
      xe = xc + xr * math.cos(ea)
      ye = yc - yr * math.sin(ea)

      lflag = 0 if abs(extent) <= 180 else 1
      sflag = 0 if extent >= 0 else 1

      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])
      
#      fh.write(u'<circle cx="{}" cy="{}" r="6" fill="{}" />\n'.format(xc, yc, rgb_to_hex((255,0,255))))
#      fh.write(u'<circle cx="{}" cy="{}" r="6" fill="{}" />\n'.format(xs, ys, rgb_to_hex((0,0,255))))
#      fh.write(u'<circle cx="{}" cy="{}" r="6" fill="{}" />\n'.format(xe, ye, rgb_to_hex((0,255,255))))
      
      fh.write(u'<path d="M{},{} A{},{} 0, {},{} {},{}" {}/>\n'.format(xs,ys, xr,yr, lflag, sflag, xe,ye, attributes))

    elif isinstance(shape, PathShape):
    
#      n0 = shape.nodes[0]
#      if len(n0) == 2:
#        c.move_to(*n0)

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
