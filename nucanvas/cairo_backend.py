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

#  @staticmethod
#  def rounded_corner(start, apex, end, rad):
#    #print('## start, apex, end', start, apex, end)
#    
#    # Translate all points with apex at origin
#    start = (start[0] - apex[0], start[1] - apex[1])
#    end = (end[0] - apex[0], end[1] - apex[1])
#    
##    print('## start, end', start, end)
#    
#    # Get angles of each line segment
#    enter_a = math.atan2(start[1], start[0]) % math.radians(360)
#    leave_a = math.atan2(end[1], end[0]) % math.radians(360)
#    
##    print('## enter, leave', math.degrees(enter_a), math.degrees(leave_a))
#    
#    bisect = abs(enter_a - (enter_a + leave_a) / 2.0)
#    
##    print('## bisect', math.degrees(bisect))
#    
#    if bisect > math.radians(82): # Nearly colinear: Skip radius
#      return (apex, apex, apex, -1)
#    
#    q = rad * math.sin(math.radians(90) - bisect) / math.sin(bisect)
#    
#    # Check that q is no more than half the shortest leg
#    enter_leg = math.sqrt(start[0]**2 + start[1]**2)
#    leave_leg = math.sqrt(end[0]**2 + end[1]**2)
#    short_leg = min(enter_leg, leave_leg)
#    if q > short_leg / 2:
#      #print('## NEW RADIUS')
#      q = short_leg / 2
#      # Compute new radius
#      rad = q * math.sin(bisect) / math.sin(math.radians(90) - bisect)
#      
#    h = math.sqrt(q**2 + rad**2)
#    
##    print('## rad, q, h', rad, q, h)
#    
#    # Center of circle
#    bisect = (enter_a + leave_a) / 2.0
# #   print('## bisect2', math.degrees(bisect))
#    center = (h * math.cos(bisect) + apex[0], h * math.sin(bisect) + apex[1])
#    
#    # Find start and end point of arcs
#    start_p = (q * math.cos(enter_a) + apex[0], q * math.sin(enter_a) + apex[1])
#    end_p = (q * math.cos(leave_a) + apex[0], q * math.sin(leave_a) + apex[1])
#    
#    return (center, start_p, end_p, rad)
    
    
#  def draw_rounded_corner(self, start, apex, end, rad, c):
#    c.line_to(*apex)
#    pth = c.copy_path()
#    
#    c.arc(start[0],start[1], 3, 0, 2 * math.pi)
#    c.stroke()
#    c.arc(apex[0],apex[1], 3, 0, 2 * math.pi)
#    c.stroke()
#    c.arc(end[0],end[1], 3, 0, 2 * math.pi)
#    c.stroke()
#    
#    center, start_p, end_p, rad = rounded_corner(start, apex, end, rad)

#    if rad < 0: # No arc
#      pass
#    else:
#      
#      c.arc(start_p[0],start_p[1], 3, 0, 2 * math.pi)
#      c.stroke()
#      c.arc(end_p[0],end_p[1], 3, 0, 2 * math.pi)
#      c.stroke()

#      
#      c.move_to(*center)
#      c.line_to(*apex)
#      c.stroke()
#      
#      # Determine angles to arc end points
#      ostart_p = (start_p[0] - center[0], start_p[1] - center[1])
#      oend_p = (end_p[0] - center[0], end_p[1] - center[1])
#      start_a = math.atan2(ostart_p[1], ostart_p[0]) % math.radians(360)
#      end_a = math.atan2(oend_p[1], oend_p[0]) % math.radians(360)
#      
#      # Determine direction of arc
#      # Rotate whole system so that start_a is on x-axis
#      # Then if delta < 180 cw  if delta > 180 ccw
#      delta = (end_a - start_a) % math.radians(360)
#      
#      print('# start_a, end_a', math.degrees(start_a), math.degrees(end_a),
#                  math.degrees(delta))

#      if delta < math.radians(180):
#        c.arc(center[0],center[1], rad, start_a, end_a)
#      else:
#        c.arc_negative(center[0],center[1], rad, start_a, end_a)
#      c.stroke()
#    
#    c.new_path()
#    c.append_path(pth)
#    
#    return end_p
    
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

#      width = shape.param('width', self.def_styles)
#      fill = shape.param('fill', self.def_styles)
#      line_color = shape.param('line_color', self.def_styles)
#      
#      stroke = True if width > 0 else False

      #print('%% RECT:', stroke, shape.options)
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
      
#      width = shape.param('width', self.def_styles)
#      fill = shape.param('fill', self.def_styles)
#      line_color = shape.param('line_color', self.def_styles)
#      
#      stroke = True if width > 0 else False

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
      #rad = abs(x1 - x0) / 2.0
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

        
      #print('%% ARC:', xc, yc, rad, start, extent)

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
    
#def render_railroad(spec, title, url_map, out_file, backend, styles, scale, transparent):
#  print('Rendering to {} using {} backend'.format(out_file, backend))
#  rc = RailCanvas(cairo_text_bbox)

#  layout = RailroadLayout(rc, styles, url_map)
#  layout.draw_diagram(spec)

#  if title is not None: # Add title
#    pos = styles.title_pos

#    x0,y0,x1,y1 = rc.bbox('all')
#    
#    tid = rc.create_text(0, 0, anchor='l', text=title, font=styles.title_font,
#      font_name='title_font')

#    tx0, ty0, tx1, ty1 = rc.bbox(tid)
#    h = ty1 - ty0
#    w = tx1 - tx0
#    
#    mx = x0 if 'l' in pos else (x1 + x0 - w) / 2  if 'c' in pos else x0 + x1 - w
#    my = (y0 - h - styles.padding) if 't' in pos else (y1 - y0 - styles.padding)

#    rc.move(tid, mx, my)

#  x0,y0,x1,y1 = rc.bbox('all')

#  W = int((x1 - x0 + 2*styles.padding) * scale)
#  H = int((y1 - y0 + 2*styles.padding) * scale)

#  if not styles.arrows: # Remove arrow heads
#    for s in rc.shapes:
#      if 'arrow' in s.options:
#        del s.options['arrow']

#  if styles.shadow: # Draw shadows first
#    bubs = [copy.deepcopy(s) for s in rc.shapes
#      if isinstance(s, BoxBubbleShape) or isinstance(s, BubbleShape) or isinstance(s, HexBubbleShape)]

#    # Remove all text and offset shadow
#    for s in bubs:
#      del s.options['text']
#      s.options['fill'] = styles.shadow_fill
#      w = s.options['width']
#      s.options['width'] = 0
#      s.move(w+1,w+1)

#    # Put rest of shapes after the shadows
#    bubs.extend(rc.shapes)
#    rc.shapes = bubs


#  if backend == 'svg':

#    # Reposition all shapes in the viewport
#    for s in rc.shapes:
#      s.move(-x0 + styles.padding, -y0 + styles.padding)

#    # Generate CSS for fonts
#    text_color = rgb_to_hex(styles.text_color)
#    css = []

#    fonts = {}
#    # Collect fonts from common styles
#    for f in [k for k in dir(styles) if k.endswith('_font')]:
#      fonts[f] = (getattr(styles, f), text_color)
#    # Collect node style fonts
#    for ns in styles.node_styles:
#      fonts[ns.name + '_font'] = (ns.font, rgb_to_hex(ns.text_color))

#    for f, fs in fonts.iteritems():
#      family, size, weight = fs[0]
#      text_color = fs[1]

#      if weight == 'italic':
#        style = 'italic'
#        weight = 'normal'
#      else:
#        style = 'normal'

#      css.append('''.{} {{fill:{}; text-anchor:middle;
#    font-family:{}; font-size:{}pt; font-weight:{}; font-style:{};}}'''.format(f,
#      text_color, family, size, weight, style))


#    font_styles = '\n'.join(css)
#    line_color = rgb_to_hex(styles.line_color)

#    with io.open(out_file, 'w', encoding='utf-8') as fh:
#      fh.write(svg_header.format(W,H, font_styles, line_color))
#      if not transparent:
#        fh.write(u'<rect width="100%" height="100%" fill="white"/>')
#      for s in rc.shapes:
#        svg_draw_shape(s, fh, styles)
#      fh.write(u'</svg>')

#  else: # Cairo backend
#    ext = os.path.splitext(out_file)[1].lower()

#    if ext == '.svg':
#      surf = cairo.SVGSurface(out_file, W, H)
#    elif ext == '.pdf':
#      surf = cairo.PDFSurface(out_file, W, H)
#    elif ext in ('.ps', '.eps'):
#      surf = cairo.PSSurface(out_file, W, H)
#      if ext == '.eps':
#        surf.set_eps(True)
#    else: # Bitmap
#      surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)

#    ctx = cairo.Context(surf)

#    if not transparent:
#      # Fill background
#      ctx.rectangle(0,0, W,H)
#      ctx.set_source_rgba(1.0,1.0,1.0)
#      ctx.fill()

#    ctx.scale(scale, scale)
#    ctx.translate(-x0 + styles.padding, -y0 + styles.padding)

#    for s in rc.shapes:
#      cairo_draw_shape(s, ctx, styles)

#    if ext in ('.svg', '.pdf', '.ps', '.eps'):
#      surf.show_page()
#    else:
#      surf.write_to_png(out_file)

