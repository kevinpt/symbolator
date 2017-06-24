# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
from __future__ import print_function

import io
import os
import math
import StringIO
import xml.etree.ElementTree as ET

from shapes import *
from cairo_backend import CairoSurface

#################################
## SVG objects
#################################

def cairo_font(tk_font):
  family, size, weight = tk_font
  return pango.FontDescription('{} {} {}'.format(family, weight, size))


def rgb_to_hex(rgb):
  return '#{:02X}{:02X}{:02X}'.format(*rgb[:3])

def hex_to_rgb(hex_color):
  v = int(hex_color[1:], 16)
  b = v & 0xFF
  g = (v >> 8) & 0xFF
  r = (v >> 16) & 0xFF
  return (r,g,b)


def xml_escape(txt):
    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def visit_shapes(s, f):
  f(s)
  try:
    for c in s.shapes:
      visit_shapes(c, f)
  except AttributeError:
    pass

class SvgSurface(BaseSurface):
  def __init__(self, fname, def_styles, padding=0, scale=1.0):
    BaseSurface.__init__(self, fname, def_styles, padding, scale)
    
    self.fh = None
    
  svg_header = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created by Symbolator http://kevinpt.github.io/symbolator -->
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xml:space="preserve"
width="{}" height="{}" viewBox="{}" version="1.1">
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
{}
</defs>
'''

  def render(self, canvas, transparent=False):
    x0,y0,x1,y1 = canvas.bbox('all')
    self.markers = canvas.markers
    
    W = x1 - x0 + 2*self.padding
    H = y1 - y0 + 2*self.padding
    
    x0 = int(x0)
    y0 = int(y0)
    
    # Reposition all shapes in the viewport
#    for s in canvas.shapes:
#      s.move(-x0 + self.padding, -y0 + self.padding)
    vbox = u' '.join(str(s) for s in (x0-self.padding,y0-self.padding, W,H))

    # Generate CSS for fonts
    text_color = rgb_to_hex(self.def_styles.text_color)

    # Get fonts from all shapes
    class FontVisitor(object):
      def __init__(self):
        self.font_ix = 1
        self.font_set = {}

      def get_font_info(self, s):
        if 'font' in s.options:
          fdef = s.options['font']
          fdata = (fdef,(0,0,0))

          if fdata not in self.font_set:
            self.font_set[fdata] = 'fnt' + str(self.font_ix)
            self.font_ix += 1
            #print('# FONT:', s.options['font'])

          fclass = self.font_set[fdata]
          s.options['css_class'] = fclass

    fv = FontVisitor()
    visit_shapes(canvas, fv.get_font_info)

    #print('## FSET:', fv.font_set)

    font_css = []
    for fs, fid in fv.font_set.iteritems():
      family, size, weight = fs[0]
      text_color = rgb_to_hex(fs[1])

      if weight == 'italic':
        style = 'italic'
        weight = 'normal'
      else:
        style = 'normal'

      font_css.append('''.{} {{fill:{};
    font-family:{}; font-size:{}pt; font-weight:{}; font-style:{};}}'''.format(fid,
      text_color, family, size, weight, style))

    font_styles = '\n'.join(font_css)

    # Determine which markers are in use
    class MarkerVisitor(object):
      def __init__(self):
        self.markers = set()

      def get_marker_info(self, s):
        mark = s.param('marker')
        if mark: self.markers.add(mark)
        mark = s.param('marker_start')
        if mark: self.markers.add(mark)
        mark = s.param('marker_segment')
        if mark: self.markers.add(mark)
        mark = s.param('marker_end')
        if mark: self.markers.add(mark)

    mv = MarkerVisitor()
    visit_shapes(canvas, mv.get_marker_info)
    used_markers = mv.markers.intersection(set(self.markers.keys()))

    # Generate markers
    markers = []
    for mname in used_markers:

      m_shape, ref, orient, units = self.markers[mname]
      mx0, my0, mx1, my1 = m_shape.bbox

      mw = mx1 - mx0
      mh = my1 - my0

      # Unfortunately it looks like browser SVG rendering doesn't properly support
      # marker viewBox that doesn't have an origin at 0,0 but Eye of Gnome does. 

      attrs = {
        'id': mname,
        'markerWidth': mw,
        'markerHeight': mh,
        'viewBox': ' '.join(str(p) for p in (0, 0, mw, mh)),
        'refX': ref[0] - mx0,
        'refY': ref[1] - my0,
        'orient': orient,
        'markerUnits': 'strokeWidth' if units == 'stroke' else 'userSpaceOnUse'
      }

      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])

      buf = StringIO.StringIO()
      self.draw_shape(m_shape, buf)
      # Shift enerything inside a group so that the viewBox origin is 0,0
      svg_shapes = '<g transform="translate({},{})">{}</g>\n'.format(-mx0, -my0, buf.getvalue())
      buf.close()

      markers.append(u'<marker {}>\n{}</marker>'.format(attributes, svg_shapes))

    markers = '\n'.join(markers)


    if self.draw_bbox:
      last = len(canvas.shapes)
      for s in canvas.shapes[:last]:
        bbox = s.bbox
        r = canvas.create_rectangle(*bbox, line_color=(255,0,0, 127), fill=(0,255,0,90))


    with io.open(self.fname, 'w', encoding='utf-8') as fh:
      self.fh = fh
      fh.write(SvgSurface.svg_header.format(int(W*self.scale),int(H*self.scale),
              vbox, font_styles, markers))
      if not transparent:
        fh.write(u'<rect x="{}" y="{}" width="100%" height="100%" fill="white"/>'.format(x0-self.padding,y0-self.padding))
      for s in canvas.shapes:
        self.draw_shape(s)
      fh.write(u'</svg>')


  def text_bbox(self, text, font_params, spacing=0):
    return CairoSurface.cairo_text_bbox(text, font_params, spacing, self.scale)

  @staticmethod
  def convert_pango_markup(text):
    t = '<X>{}</X>'.format(text)
    root = ET.fromstring(t)
    # Convert <span> to <tspan>
    for child in root:
      if child.tag == 'span':
        child.tag = 'tspan'
        if 'foreground' in child.attrib:
          child.attrib['fill'] = child.attrib['foreground']
          del child.attrib['foreground']
    return ET.tostring(root)[3:-4].decode('utf-8')

  @staticmethod
  def draw_text(x, y, text, css_class, text_color, baseline, anchor, anchor_off, spacing, fh):
    ah, av = anchor
    
    if ah == 'w':
      text_anchor = 'normal'
    elif ah == 'e':
      text_anchor = 'end'
    else:
      text_anchor = 'middle'

    attrs = {
      'text-anchor': text_anchor,
      'dy': baseline + anchor_off[1]
    }


    if text_color != (0,0,0):
      attrs['style'] = 'fill:{}'.format(rgb_to_hex(text_color))

    attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])

    text = SvgSurface.convert_pango_markup(text)

    fh.write(u'<text class="{}" x="{}" y="{}" {}>{}</text>\n'.format(css_class, x, y, attributes, text))


  def draw_shape(self, shape, fh=None):
    if fh is None:
      fh = self.fh
    default_pen = rgb_to_hex(self.def_styles.line_color)
    
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
      baseline = shape._baseline
      
      text = shape.param('text', self.def_styles)      
      font = shape.param('font', self.def_styles)
      text_color = shape.param('text_color', self.def_styles)
      #anchor = shape.param('anchor', self.def_styles).lower()
      spacing = shape.param('spacing', self.def_styles)
      css_class = shape.param('css_class')
      
      anchor = shape.anchor_decode
      anchor_off = shape._anchor_off
      SvgSurface.draw_text(x0, y0, text, css_class, text_color, baseline, anchor, anchor_off, spacing, fh)
      

    elif isinstance(shape, LineShape):
      x0, y0, x1, y1 = shape.points
      
      marker = shape.param('marker')
      marker_start = shape.param('marker_start')
      marker_seg = shape.param('marker_segment')
      marker_end = shape.param('marker_end')
      if marker is not None:
        if marker_start is None:
          marker_start = marker
        if marker_end is None:
          marker_end = marker
        if marker_seg is None:
          marker_seg = marker
          
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
          if units == 'stroke' and width > 0:
            soff *= width
          
          # Move start point
          x0 += soff * dx
          y0 += soff * dy

        if marker_end in self.markers:
          # Get bbox of marker
          m_shape, ref, orient, units = self.markers[marker_end]
          mx0, my0, mx1, my1 = m_shape.bbox
          eoff = (mx1 - ref[0]) * adjust
          if units == 'stroke' and width > 0:
            eoff *= width
          
          # Move end point
          x1 -= eoff * dx
          y1 -= eoff * dy


      # Add markers
      if marker_start in self.markers:
        attrs['marker-start'] = u'url(#{})'.format(marker_start)
      if marker_end in self.markers:
        attrs['marker-end'] = u'url(#{})'.format(marker_end)
      # FIXME: marker_seg

      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])

      fh.write(u'<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>\n'.format(x0,y0, x1,y1, attributes))


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

      closed = 'z' if shape.options['closed'] else ''
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

      fh.write(u'<path d="M{},{} A{},{} 0, {},{} {},{} {}" {}/>\n'.format(xs,ys, xr,yr, lflag, sflag, xe,ye, closed, attributes))

    elif isinstance(shape, PathShape):
      pp = shape.nodes[0]
      nl = []

      for i, n in enumerate(shape.nodes):
        if n == 'z':
          nl.append('z')
          break
        elif len(n) == 2:
          cmd = 'L' if i > 0 else 'M'
          nl.append('{} {} {}'.format(cmd, *n))
          pp = n
        elif len(n) == 6:
          nl.append('C {} {}, {} {}, {} {}'.format(*n))
          pp = n[4:6]
        elif len(n) == 5: # Arc (javascript arcto() args)
          #print('# arc:', pp)
          #pp = self.draw_rounded_corner(pp, n[0:2], n[2:4], n[4], c)
          
          center, start_p, end_p, rad = rounded_corner(pp, n[0:2], n[2:4], n[4])
          if rad < 0: # No arc
            print('## Rad < 0')
            #c.line_to(*end_p)
            nl.append('L {} {}'.format(*end_p))
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
            
            if delta < math.radians(180): # CW
              sflag = 1
            else: # CCW
              sflag = 0

            nl.append('L {} {}'.format(*start_p))
            #nl.append('L {} {}'.format(*end_p))
            nl.append('A {} {} 0 0 {} {} {}'.format(rad, rad, sflag, *end_p))


            #print('# start_a, end_a', math.degrees(start_a), math.degrees(end_a),
            #            math.degrees(delta))
            #fh.write(u'<circle cx="{}" cy="{}" r="{}" stroke="#F00" stroke-width="1" fill="none"/>\n'.format(center[0], center[1], rad))
          pp = end_p
          
          #print('# pp:', pp)

      attributes = ' '.join(['{}="{}"'.format(k,v) for k,v in attrs.iteritems()])
      fh.write(u'<path d="{}" {}/>\n'.format(' '.join(nl), attributes))

