#!/usr/bin/python

from __future__ import print_function

#import os
#import math

from shapes import GroupShape, DrawStyle
#from cairo_backend import CairoSurface
#import cairo

#try:
#  import pango
#  import pangocairo
#  use_pygobject = False
#except ImportError:
#  from gi.repository import Pango as pango
#  from gi.repository import PangoCairo as pangocairo
#  use_pygobject = True



##################################
### CAIRO objects
##################################

#def rgb_to_cairo(rgb):
#  if len(rgb) == 4:
#    r,g,b,a = rgb
#    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)

#  else:
#    r,g,b = rgb
#    return (r / 255.0, g / 255.0, b / 255.0, 1.0)

#def cairo_font(tk_font):
#  family, size, weight = tk_font
#  return pango.FontDescription('{} {} {}'.format(family, weight, size))


#def cairo_line_cap(line_cap):
#  if line_cap == 'round':
#    return cairo.LINE_CAP_ROUND
#  elif line_cap == 'square':
#    return cairo.LINE_CAP_SQUARE
#  else:
#    return cairo.LINE_CAP_BUTT


#class BaseSurface(object):
#  def __init__(self, fname, def_styles, padding=0, scale=1.0):
#    self.fname = fname
#    self.def_styles = def_styles
#    self.padding = padding
#    self.scale = scale
#    self.draw_bbox = False
#    self.markers = {}
#    
#    self.shape_drawers = {}
#    
#  def add_shape_class(self, sclass, drawer):
#    self.shape_drawers[sclass] = drawer
#    
#  def render(self, canvas, transparent=False):
#    pass
#    
#  def text_bbox(self, text, font_params):
#    pass

#    
#class CairoSurface(BaseSurface):
#  def __init__(self, fname, def_styles, padding=0, scale=1.0):
#    BaseSurface.__init__(self, fname, def_styles, padding, scale)
#    self.ctx = None
#    
#  def render(self, canvas, transparent=False):
#  
#    x0,y0,x1,y1 = canvas.bbox('all')
#    self.markers = canvas.markers
#    
#    W = int((x1 - x0 + 2*self.padding) * self.scale)
#    H = int((y1 - y0 + 2*self.padding) * self.scale)
#  
#    ext = os.path.splitext(self.fname)[1].lower()

#    if ext == '.svg':
#      surf = cairo.SVGSurface(self.fname, W, H)
#    elif ext == '.pdf':
#      surf = cairo.PDFSurface(self.fname, W, H)
#    elif ext in ('.ps', '.eps'):
#      surf = cairo.PSSurface(self.fname, W, H)
#      if ext == '.eps':
#        surf.set_eps(True)
#    else: # Bitmap
#      surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)

#    self.ctx = cairo.Context(surf)
#    ctx = self.ctx

#    if not transparent:
#      # Fill background
#      ctx.rectangle(0,0, W,H)
#      ctx.set_source_rgba(1.0,1.0,1.0)
#      ctx.fill()

#    ctx.scale(self.scale, self.scale)
#    ctx.translate(-x0 + self.padding, -y0 + self.padding)

#    if self.draw_bbox:
#      last = len(canvas.shapes)
#      for s in canvas.shapes[:last]:
#        bbox = s.bbox
#        r = canvas.create_rectangle(*bbox, line_color=(255,0,0, 127), fill=(0,255,0,90))

#    for s in canvas.shapes:
#      self.draw_shape(s)


#    if ext in ('.svg', '.pdf', '.ps', '.eps'):
#      surf.show_page()
#    else:
#      surf.write_to_png(self.fname)


#  def text_bbox(self, text, font_params, spacing = 0):
#    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
#    ctx = cairo.Context(surf)
#    # FIXME: Syntrax bug
#    # The scaling must match the final context.
#    # If not there can be a mismatch between the computed extents here
#    # and those generated for the final render.
#    ctx.scale(self.scale, self.scale)
#    
#    font = cairo_font(font_params)
#    
#    

#    if use_pygobject:
#      status, attrs, plain_text, _ = pango.parse_markup(text, len(text), '\0')
#      
#      layout = pangocairo.create_layout(ctx)
#      pctx = layout.get_context()
#      fo = cairo.FontOptions()
#      fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
#      pangocairo.context_set_font_options(pctx, fo)
#      layout.set_font_description(font)
#      layout.set_spacing(spacing * pango.SCALE)
#      layout.set_text(plain_text, len(plain_text))
#      layout.set_attributes(attrs)
#      re = layout.get_pixel_extents()[1] # Get logical extents
#      extents = (re.x, re.y, re.x + re.width, re.y + re.height)

#    else: # pyGtk
#      attrs, plain_text, _ = pango.parse_markup(text)
#    
#      pctx = pangocairo.CairoContext(ctx)
#      pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
#      layout = pctx.create_layout()
#      layout.set_font_description(font)
#      layout.set_spacing(spacing * pango.SCALE)
#      layout.set_text(plain_text)
#      layout.set_attributes(attrs)
#      
#      #print('@@ EXTENTS:', layout.get_pixel_extents()[1], spacing)
#      extents = layout.get_pixel_extents()[1] # Get logical extents
#    w = extents[2] - extents[0]
#    h = extents[3] - extents[1]
#    x0 = - w // 2.0
#    y0 = - h // 2.0
#    return [x0,y0, x0+w,y0+h]



#  @staticmethod
#  def draw_text(x, y, text, font, text_color, spacing, c):
#    c.save()
#    #print('## TEXT COLOR:', text_color)
#    c.set_source_rgba(*rgb_to_cairo(text_color))
#    font = cairo_font(font)

#    c.translate(x, y)
#    
#    if use_pygobject:
#      status, attrs, plain_text, _ = pango.parse_markup(text, len(text), '\0')
#      
#      layout = pangocairo.create_layout(c)
#      pctx = layout.get_context()
#      fo = cairo.FontOptions()
#      fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
#      pangocairo.context_set_font_options(pctx, fo)
#      layout.set_font_description(font)
#      layout.set_spacing(spacing * pango.SCALE)
#      layout.set_text(plain_text, len(plain_text))
#      layout.set_attributes(attrs)
#      pangocairo.update_layout(c, layout)
#      pangocairo.show_layout(c, layout)

#    else: # pyGtk
#      attrs, plain_text, _ = pango.parse_markup(text)
#      
#      pctx = pangocairo.CairoContext(c)
#      pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
#      layout = pctx.create_layout()
#      layout.set_font_description(font)
#      layout.set_spacing(spacing * pango.SCALE)
#      layout.set_text(plain_text)
#      layout.set_attributes(attrs)
#      pctx.update_layout(layout)
#      pctx.show_layout(layout)
#      
#    c.restore()

##  @staticmethod
##  def rounded_corner(start, apex, end, rad):
##    #print('## start, apex, end', start, apex, end)
##    
##    # Translate all points with apex at origin
##    start = (start[0] - apex[0], start[1] - apex[1])
##    end = (end[0] - apex[0], end[1] - apex[1])
##    
###    print('## start, end', start, end)
##    
##    # Get angles of each line segment
##    enter_a = math.atan2(start[1], start[0]) % math.radians(360)
##    leave_a = math.atan2(end[1], end[0]) % math.radians(360)
##    
###    print('## enter, leave', math.degrees(enter_a), math.degrees(leave_a))
##    
##    bisect = abs(enter_a - (enter_a + leave_a) / 2.0)
##    
###    print('## bisect', math.degrees(bisect))
##    
##    if bisect > math.radians(82): # Nearly colinear: Skip radius
##      return (apex, apex, apex, -1)
##    
##    q = rad * math.sin(math.radians(90) - bisect) / math.sin(bisect)
##    
##    # Check that q is no more than half the shortest leg
##    enter_leg = math.sqrt(start[0]**2 + start[1]**2)
##    leave_leg = math.sqrt(end[0]**2 + end[1]**2)
##    short_leg = min(enter_leg, leave_leg)
##    if q > short_leg / 2:
##      #print('## NEW RADIUS')
##      q = short_leg / 2
##      # Compute new radius
##      rad = q * math.sin(bisect) / math.sin(math.radians(90) - bisect)
##      
##    h = math.sqrt(q**2 + rad**2)
##    
###    print('## rad, q, h', rad, q, h)
##    
##    # Center of circle
##    bisect = (enter_a + leave_a) / 2.0
## #   print('## bisect2', math.degrees(bisect))
##    center = (h * math.cos(bisect) + apex[0], h * math.sin(bisect) + apex[1])
##    
##    # Find start and end point of arcs
##    start_p = (q * math.cos(enter_a) + apex[0], q * math.sin(enter_a) + apex[1])
##    end_p = (q * math.cos(leave_a) + apex[0], q * math.sin(leave_a) + apex[1])
##    
##    return (center, start_p, end_p, rad)
#    
#    
##  def draw_rounded_corner(self, start, apex, end, rad, c):
##    c.line_to(*apex)
##    pth = c.copy_path()
##    
##    c.arc(start[0],start[1], 3, 0, 2 * math.pi)
##    c.stroke()
##    c.arc(apex[0],apex[1], 3, 0, 2 * math.pi)
##    c.stroke()
##    c.arc(end[0],end[1], 3, 0, 2 * math.pi)
##    c.stroke()
##    
##    center, start_p, end_p, rad = rounded_corner(start, apex, end, rad)

##    if rad < 0: # No arc
##      pass
##    else:
##      
##      c.arc(start_p[0],start_p[1], 3, 0, 2 * math.pi)
##      c.stroke()
##      c.arc(end_p[0],end_p[1], 3, 0, 2 * math.pi)
##      c.stroke()

##      
##      c.move_to(*center)
##      c.line_to(*apex)
##      c.stroke()
##      
##      # Determine angles to arc end points
##      ostart_p = (start_p[0] - center[0], start_p[1] - center[1])
##      oend_p = (end_p[0] - center[0], end_p[1] - center[1])
##      start_a = math.atan2(ostart_p[1], ostart_p[0]) % math.radians(360)
##      end_a = math.atan2(oend_p[1], oend_p[0]) % math.radians(360)
##      
##      # Determine direction of arc
##      # Rotate whole system so that start_a is on x-axis
##      # Then if delta < 180 cw  if delta > 180 ccw
##      delta = (end_a - start_a) % math.radians(360)
##      
##      print('# start_a, end_a', math.degrees(start_a), math.degrees(end_a),
##                  math.degrees(delta))

##      if delta < math.radians(180):
##        c.arc(center[0],center[1], rad, start_a, end_a)
##      else:
##        c.arc_negative(center[0],center[1], rad, start_a, end_a)
##      c.stroke()
##    
##    c.new_path()
##    c.append_path(pth)
##    
##    return end_p
#    
#  def draw_marker(self, name, mp, tp, width, c):
#    if name in self.markers:
#      #print('# MARKER:', name)
#      m_shape, ref, orient, units = self.markers[name]

#      c.save()
#      c.translate(*mp)
#      if orient == 'auto':
#        angle = math.atan2(tp[1]-mp[1], tp[0]-mp[0])
#        c.rotate(angle)
#      elif isinstance(orient, int):
#        angle = math.radians(orient)
#        c.rotate(angle)

#      if units == 'stroke':
#        print('  SCALE:', width)
#        c.scale(width,width)
#        
#      c.translate(-ref[0], -ref[1])
#      
#      
#      self.draw_shape(m_shape)
#      c.restore()
#    
#  def draw_shape(self, shape):
#    c = self.ctx
#    default_pen = rgb_to_cairo(self.def_styles.line_color)
#    c.set_source_rgba(*default_pen)

#    width = shape.param('width', self.def_styles)
#    fill = shape.param('fill', self.def_styles)
#    line_color = shape.param('line_color', self.def_styles)
#    line_cap = cairo_line_cap(shape.param('line_cap', self.def_styles))
#    
#    stroke = True if width > 0 else False

#    c.set_line_width(width)
#    c.set_line_cap(line_cap)

#    if shape.__class__ in self.shape_drawers:
#      self.shape_drawers[shape.__class__](shape, self)
#    
#    elif isinstance(shape, GroupShape):
#      c.save()
#      c.translate(*shape._pos)
#      if 'scale' in shape.options:
#        c.scale(shape.options['scale'], shape.options['scale'])
#      if 'angle' in shape.options:
#        c.rotate(math.radians(shape.options['angle']))

#      for s in shape.shapes:
#        self.draw_shape(s)
#      c.restore()

#    elif isinstance(shape, TextShape):
#      x0, y0, x1, y1 = shape.points
#      
#      text = shape.param('text', self.def_styles)      
#      font = shape.param('font', self.def_styles)
#      text_color = shape.param('text_color', self.def_styles)
#      anchor = shape.param('anchor', self.def_styles).lower()
#      spacing = shape.param('spacing', self.def_styles)
#      
#      CairoSurface.draw_text(x0, y0, text, font, text_color, spacing, c)
#      

#    elif isinstance(shape, LineShape):
#      x0, y0, x1, y1 = shape.points
#      
#      marker = shape.param('marker')
#      marker_start = shape.param('marker_start')
#      marker_mid = shape.param('marker_mid')
#      marker_end = shape.param('marker_end')
#      if marker is not None:
#        if marker_start is None:
#          marker_start = marker
#        if marker_end is None:
#          marker_end = marker
#        if marker_mid is None:
#          marker_mid = marker
#          
#      adjust = shape.param('marker_adjust')
#      if adjust is None:
#        adjust = 0
#        
#      if adjust > 0:
#        angle = math.atan2(y1-y0, x1-x0)
#        dx = math.cos(angle)
#        dy = math.sin(angle)
#        
#        if marker_start in self.markers:
#          # Get bbox of marker
#          m_shape, ref, orient, units = self.markers[marker_start]
#          mx0, my0, mx1, my1 = m_shape.bbox
#          soff = (ref[0] - mx0) * adjust
#          #print("# SOFF", mx0, ref[0], soff)
#          
#          # Move start point
#          x0 += soff * dx
#          y0 += soff * dy

#        if marker_end in self.markers:
#          # Get bbox of marker
#          m_shape, ref, orient, units = self.markers[marker_end]
#          mx0, my0, mx1, my1 = m_shape.bbox
#          eoff = (mx1 - ref[0]) * adjust
#          #print("# EOFF", mx1, ref[0], eoff)
#          
#          # Move end point
#          x1 -= eoff * dx
#          y1 -= eoff * dy


#      c.move_to(x0,y0)
#      c.line_to(x1,y1)
#      c.stroke()

#      # Draw any markers

#      self.draw_marker(marker_start, (x0,y0), (x1,y1), width, c)
#      self.draw_marker(marker_end, (x1,y1), (x1 + 2*(x1-x0),y1 + 2*(y1-y0)), width,  c)
#      self.draw_marker(marker_mid, ((x0 + x1)/2,(y0+y1)/2), (x1,y1), width, c)


#    elif isinstance(shape, RectShape):
#      x0, y0, x1, y1 = shape.points
#      c.rectangle(x0,y0, x1-x0,y1-y0)

##      width = shape.param('width', self.def_styles)
##      fill = shape.param('fill', self.def_styles)
##      line_color = shape.param('line_color', self.def_styles)
##      
##      stroke = True if width > 0 else False

#      #print('%% RECT:', stroke, shape.options)
#      if fill is not None:
#        c.set_source_rgba(*rgb_to_cairo(fill))
#        if stroke:
#          c.fill_preserve()
#        else:
#          c.fill()

#      if stroke:
#        c.set_source_rgba(*rgb_to_cairo(line_color))
#        c.stroke()


#    elif isinstance(shape, OvalShape):
#      x0, y0, x1, y1 = shape.points
#      xc = (x0 + x1) / 2.0
#      yc = (y0 + y1) / 2.0
#      w = abs(x1 - x0)
#      h = abs(y1 - y0)
#      
#      c.save()
#      # Set transformation matrix to permit drawing ovals
#      c.translate(xc,yc)
#      c.scale(w/2.0, h/2.0)
#      c.arc(0,0, 1, 0, 2 * math.pi)
#      #c.arc(xc,yc, rad, 0, 2 * math.pi)
#      
##      width = shape.param('width', self.def_styles)
##      fill = shape.param('fill', self.def_styles)
##      line_color = shape.param('line_color', self.def_styles)
##      
##      stroke = True if width > 0 else False

#      if fill is not None:
#        c.set_source_rgba(*rgb_to_cairo(fill))
#        if stroke:
#          c.fill_preserve()
#        else:
#          c.fill()

#      c.restore() # Stroke with original transform

#      if stroke:
#        c.set_source_rgba(*rgb_to_cairo(line_color))
#        c.stroke()



#    elif isinstance(shape, ArcShape):
#      x0, y0, x1, y1 = shape.points
#      xc = (x0 + x1) / 2.0
#      yc = (y0 + y1) / 2.0
#      #rad = abs(x1 - x0) / 2.0
#      w = abs(x1 - x0)
#      h = abs(y1 - y0)

#      start = shape.options['start']
#      extent = shape.options['extent']

#      # Start and end angles
#      sa = -math.radians(start)
#      ea = -math.radians(start + extent)

#      # Tk has opposite angle convention from Cairo
#      #   Positive extent is a negative rotation in Cairo
#      #   Negative extent is a positive rotation in Cairo
#      
#      c.save()
#      
#      c.translate(xc, yc)
#      c.scale(w/2.0, h/2.0)
#        
#      if fill is not None:
#        c.move_to(0,0)
#        if extent >= 0:
#          c.arc_negative(0,0, 1.0, sa, ea)
#        else:
#          c.arc(0,0, 1.0, sa, ea)
#        c.set_source_rgba(*rgb_to_cairo(fill))
#        c.fill()
#        

#      # Stroke arc segment
#      c.new_sub_path()
#      if extent >= 0:
#        c.arc_negative(0,0, 1.0, sa, ea)
#      else:
#        c.arc(0,0, 1.0, sa, ea)

#      c.restore()
#      c.set_source_rgba(*rgb_to_cairo(line_color))
#      c.stroke()

#        
#      #print('%% ARC:', xc, yc, rad, start, extent)

#    elif isinstance(shape, PathShape):
#    
##      n0 = shape.nodes[0]
##      if len(n0) == 2:
##        c.move_to(*n0)

#      pp = shape.nodes[0]

#      for n in shape.nodes:
#        if n == 'z':
#          c.close_path()
#          break
#        elif len(n) == 2:
#          c.line_to(*n)
#          pp = n
#        elif len(n) == 6:
#          c.curve_to(*n)
#          pp = n[4:6]
#        elif len(n) == 5: # Arc (javascript arcto() args)
#          #print('# arc:', pp)
#          #pp = self.draw_rounded_corner(pp, n[0:2], n[2:4], n[4], c)
#          
#          center, start_p, end_p, rad = rounded_corner(pp, n[0:2], n[2:4], n[4])
#          if rad < 0: # No arc
#            c.line_to(*end_p)
#          else:
#            # Determine angles to arc end points
#            ostart_p = (start_p[0] - center[0], start_p[1] - center[1])
#            oend_p = (end_p[0] - center[0], end_p[1] - center[1])
#            start_a = math.atan2(ostart_p[1], ostart_p[0]) % math.radians(360)
#            end_a = math.atan2(oend_p[1], oend_p[0]) % math.radians(360)
#            
#            # Determine direction of arc
#            # Rotate whole system so that start_a is on x-axis
#            # Then if delta < 180 cw  if delta > 180 ccw
#            delta = (end_a - start_a) % math.radians(360)
#            
#            #print('# start_a, end_a', math.degrees(start_a), math.degrees(end_a),
#            #            math.degrees(delta))

#            if delta < math.radians(180): # CW
#              c.arc(center[0],center[1], rad, start_a, end_a)
#            else: # CCW
#              c.arc_negative(center[0],center[1], rad, start_a, end_a)
#          pp = end_p
#          
#          #print('# pp:', pp)
#          

#      if fill is not None:
#        c.set_source_rgba(*rgb_to_cairo(fill))
#        if stroke:
#          c.fill_preserve()
#        else:
#          c.fill()

#      if stroke:
#        c.set_source_rgba(*rgb_to_cairo(line_color))
#        c.stroke()
#    
##def render_railroad(spec, title, url_map, out_file, backend, styles, scale, transparent):
##  print('Rendering to {} using {} backend'.format(out_file, backend))
##  rc = RailCanvas(cairo_text_bbox)

##  layout = RailroadLayout(rc, styles, url_map)
##  layout.draw_diagram(spec)

##  if title is not None: # Add title
##    pos = styles.title_pos

##    x0,y0,x1,y1 = rc.bbox('all')
##    
##    tid = rc.create_text(0, 0, anchor='l', text=title, font=styles.title_font,
##      font_name='title_font')

##    tx0, ty0, tx1, ty1 = rc.bbox(tid)
##    h = ty1 - ty0
##    w = tx1 - tx0
##    
##    mx = x0 if 'l' in pos else (x1 + x0 - w) / 2  if 'c' in pos else x0 + x1 - w
##    my = (y0 - h - styles.padding) if 't' in pos else (y1 - y0 - styles.padding)

##    rc.move(tid, mx, my)

##  x0,y0,x1,y1 = rc.bbox('all')

##  W = int((x1 - x0 + 2*styles.padding) * scale)
##  H = int((y1 - y0 + 2*styles.padding) * scale)

##  if not styles.arrows: # Remove arrow heads
##    for s in rc.shapes:
##      if 'arrow' in s.options:
##        del s.options['arrow']

##  if styles.shadow: # Draw shadows first
##    bubs = [copy.deepcopy(s) for s in rc.shapes
##      if isinstance(s, BoxBubbleShape) or isinstance(s, BubbleShape) or isinstance(s, HexBubbleShape)]

##    # Remove all text and offset shadow
##    for s in bubs:
##      del s.options['text']
##      s.options['fill'] = styles.shadow_fill
##      w = s.options['width']
##      s.options['width'] = 0
##      s.move(w+1,w+1)

##    # Put rest of shapes after the shadows
##    bubs.extend(rc.shapes)
##    rc.shapes = bubs


##  if backend == 'svg':

##    # Reposition all shapes in the viewport
##    for s in rc.shapes:
##      s.move(-x0 + styles.padding, -y0 + styles.padding)

##    # Generate CSS for fonts
##    text_color = rgb_to_hex(styles.text_color)
##    css = []

##    fonts = {}
##    # Collect fonts from common styles
##    for f in [k for k in dir(styles) if k.endswith('_font')]:
##      fonts[f] = (getattr(styles, f), text_color)
##    # Collect node style fonts
##    for ns in styles.node_styles:
##      fonts[ns.name + '_font'] = (ns.font, rgb_to_hex(ns.text_color))

##    for f, fs in fonts.iteritems():
##      family, size, weight = fs[0]
##      text_color = fs[1]

##      if weight == 'italic':
##        style = 'italic'
##        weight = 'normal'
##      else:
##        style = 'normal'

##      css.append('''.{} {{fill:{}; text-anchor:middle;
##    font-family:{}; font-size:{}pt; font-weight:{}; font-style:{};}}'''.format(f,
##      text_color, family, size, weight, style))


##    font_styles = '\n'.join(css)
##    line_color = rgb_to_hex(styles.line_color)

##    with io.open(out_file, 'w', encoding='utf-8') as fh:
##      fh.write(svg_header.format(W,H, font_styles, line_color))
##      if not transparent:
##        fh.write(u'<rect width="100%" height="100%" fill="white"/>')
##      for s in rc.shapes:
##        svg_draw_shape(s, fh, styles)
##      fh.write(u'</svg>')

##  else: # Cairo backend
##    ext = os.path.splitext(out_file)[1].lower()

##    if ext == '.svg':
##      surf = cairo.SVGSurface(out_file, W, H)
##    elif ext == '.pdf':
##      surf = cairo.PDFSurface(out_file, W, H)
##    elif ext in ('.ps', '.eps'):
##      surf = cairo.PSSurface(out_file, W, H)
##      if ext == '.eps':
##        surf.set_eps(True)
##    else: # Bitmap
##      surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)

##    ctx = cairo.Context(surf)

##    if not transparent:
##      # Fill background
##      ctx.rectangle(0,0, W,H)
##      ctx.set_source_rgba(1.0,1.0,1.0)
##      ctx.fill()

##    ctx.scale(scale, scale)
##    ctx.translate(-x0 + styles.padding, -y0 + styles.padding)

##    for s in rc.shapes:
##      cairo_draw_shape(s, ctx, styles)

##    if ext in ('.svg', '.pdf', '.ps', '.eps'):
##      surf.show_page()
##    else:
##      surf.write_to_png(out_file)


##################################
### NuCANVAS objects
##################################


#def rounded_corner(start, apex, end, rad):
#  #print('## start, apex, end', start, apex, end)
#  
#  # Translate all points with apex at origin
#  start = (start[0] - apex[0], start[1] - apex[1])
#  end = (end[0] - apex[0], end[1] - apex[1])
#  
##    print('## start, end', start, end)
#  
#  # Get angles of each line segment
#  enter_a = math.atan2(start[1], start[0]) % math.radians(360)
#  leave_a = math.atan2(end[1], end[0]) % math.radians(360)
#  
##    print('## enter, leave', math.degrees(enter_a), math.degrees(leave_a))
#  
#  bisect = abs(enter_a - (enter_a + leave_a) / 2.0)
#  
##    print('## bisect', math.degrees(bisect))
#  
#  if bisect > math.radians(82): # Nearly colinear: Skip radius
#    return (apex, apex, apex, -1)
#  
#  q = rad * math.sin(math.radians(90) - bisect) / math.sin(bisect)
#  
#  # Check that q is no more than half the shortest leg
#  enter_leg = math.sqrt(start[0]**2 + start[1]**2)
#  leave_leg = math.sqrt(end[0]**2 + end[1]**2)
#  short_leg = min(enter_leg, leave_leg)
#  if q > short_leg / 2:
#    #print('## NEW RADIUS')
#    q = short_leg / 2
#    # Compute new radius
#    rad = q * math.sin(bisect) / math.sin(math.radians(90) - bisect)
#    
#  h = math.sqrt(q**2 + rad**2)
#  
##    print('## rad, q, h', rad, q, h)
#  
#  # Center of circle
#  bisect = (enter_a + leave_a) / 2.0
##   print('## bisect2', math.degrees(bisect))
#  center = (h * math.cos(bisect) + apex[0], h * math.sin(bisect) + apex[1])
#  
#  # Find start and end point of arcs
#  start_p = (q * math.cos(enter_a) + apex[0], q * math.sin(enter_a) + apex[1])
#  end_p = (q * math.cos(leave_a) + apex[0], q * math.sin(leave_a) + apex[1])
#  
#  return (center, start_p, end_p, rad)



#class DrawStyle(object):
#  def __init__(self):
#    # Set defaults
#    self.width = 1
#    self.line_color = (0,0,255)
#    self.line_cap = 'butt'
##    self.arrows = True
#    self.fill = None
#    self.text_color = (0,0,0)
#    self.font = ('Helvetica', 12, 'normal')
#    self.anchor = 'center'



#class BaseShape(object):
#  def __init__(self, options, **kwargs):
#    #self.options = {}
#    self.options = {} if options is None else options
#    self.options.update(kwargs)
#    
#    self._bbox = [0,0,1,1]
#    self.tags = set()

#  @property
#  def points(self):
#    return tuple(self._bbox)

#  @property
#  def bbox(self):
#    if 'width' in self.options:
#      w = self.options['width'] / 2.0
#    else:
#      w = 0

#    # FIXME: Syntrax has a bug in this prop. Fix is below
#    x0 = min(self._bbox[0], self._bbox[2])
#    x1 = max(self._bbox[0], self._bbox[2])
#    y0 = min(self._bbox[1], self._bbox[3])
#    y1 = max(self._bbox[1], self._bbox[3])
#    
#    x0 -= w
#    x1 += w
#    y0 -= w
#    y1 += w

#    return (x0,y0,x1,y1)

#  def param(self, name, def_styles=None):
#    if name in self.options:
#      return self.options[name]
#    elif def_styles is not None:
#      return getattr(def_styles, name)
#    else:
#      return None


#  def is_tagged(self, item):
#    return item in self.tags

#  def update_tags(self):
#    if 'tags' in self.options:
#      self.tags = self.tags.union(self.options['tags'])
#      del self.options['tags']

#  def move(self, dx, dy):
#    if self._bbox is not None:
#      self._bbox[0] += dx
#      self._bbox[1] += dy
#      self._bbox[2] += dx
#      self._bbox[3] += dy

#  def dtag(self, tag=None):
#    if tag is None:
#      self.tags.clear()
#    else:
#      self.tags.discard(tag)

#  def addtag(self, tag=None):
#    if tag is not None:
#      self.tags.add(tag)

#  def draw(self, c):
#    pass


#def rotate_bbox(box, a):
#  corners = ( (box[0], box[1]), (box[0], box[3]), (box[2], box[3]), (box[2], box[1]) )
#  a = -math.radians(a)
#  sa = math.sin(a)
#  ca = math.cos(a)
#  
#  rot = []
#  for p in corners:
#    rx = p[0]*ca + p[1]*sa
#    ry = -p[0]*sa + p[1]*ca
#    rot.append((rx,ry))
#  
#  rot = list(zip(*rot))
#  rx0 = min(rot[0])
#  rx1 = max(rot[0])
#  ry0 = min(rot[1])
#  ry1 = max(rot[1])

#  #print('## RBB:', box, rot)
#    
#  return (rx0, ry0, rx1, ry1)

#class GroupShape(BaseShape):
#  def __init__(self, surf, x0, y0, options, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._pos = (x0,y0)
#    self._bbox = None
#    self.shapes = []
#    self.surf = surf
#    
#    self.parent = None
#    if 'parent' in options:
#      self.parent = options['parent']
#      del options['parent']
#    
#    self.update_tags()
#    
#  def ungroup(self):
#    if self.parent is None:
#      return
#    
#    x, y = self._pos
#    for s in self.shapes:
#      s.move(x, y)
#      if isinstance(s, GroupShape):
#        s.parent = self.parent

#    # Transfer group children to our parent
#    pshapes = self.parent.shapes
#    pos = pshapes.index(self)

#    # Remove this group
#    self.parent.shapes = pshapes[:pos] + self.shapes + pshapes[pos+1:]
#    
#  def ungroup_all(self):
#    for s in self.shapes:
#      if isinstance(s, GroupShape):
#        s.ungroup_all()
#    self.ungroup()    
#    
#  def move(self, dx, dy):
#    BaseShape.move(self, dx, dy)
#    self._pos = (self._pos[0] + dx, self._pos[1] + dy)
#    
#  def create_shape(self, sclass, x0, y0, x1, y1, **options):
#    shape = sclass(x0, y0, x1, y1, options)
#    self.shapes.append(shape)
#    self._bbox = None # Invalidate memoized box
#    return shape

#  def create_group(self, x0, y0, **options):
#    options['parent'] = self
#    shape = GroupShape(self.surf, x0, y0, options)
#    self.shapes.append(shape)
#    self._bbox = None # Invalidate memoized box
#    return shape


#  def create_arc(self, x0, y0, x1, y1, **options):
#    return self.create_shape(ArcShape, x0, y0, x1, y1, **options)

#  def create_line(self, x0, y0, x1, y1, **options):
#    return self.create_shape(LineShape, x0, y0, x1, y1, **options)

#  def create_oval(self, x0, y0, x1, y1, **options):
#    return self.create_shape(OvalShape, x0, y0, x1, y1, **options)

#  def create_rectangle(self, x0, y0, x1, y1, **options):
#    return self.create_shape(RectShape, x0, y0, x1, y1, **options)

#  def create_text(self, x0, y0, **options):
#  
#    # Must set default font now so we can use its metrics to get bounding box
#    if 'font' not in options:
#      options['font'] = self.surf.def_styles.font
#  
#    shape = TextShape(x0, y0, self.surf, options)
#    self.shapes.append(shape)
#    self._bbox = None # Invalidate memoized box

#    # Add a unique tag to serve as an ID
#    id_tag = 'id' + str(TextShape.next_text_id)
#    shape.tags.add(id_tag)
#    #return id_tag # FIXME
#    return shape
#    
#  def create_path(self, nodes, **options):
#    shape = PathShape(nodes, options)
#    self.shapes.append(shape)
#    self._bbox = None # Invalidate memoized box
#    return shape

#    
#  @property
#  def bbox(self):
#    if self._bbox is None:
#      bx0 = 0
#      bx1 = 0
#      by0 = 0
#      by1 = 0

#      boxes = [s.bbox for s in self.shapes]
#      boxes = list(zip(*boxes))
#      if len(boxes) > 0:
#        bx0 = min(boxes[0])
#        by0 = min(boxes[1])
#        bx1 = max(boxes[2])
#        by1 = max(boxes[3])
#        
#      if 'scale' in self.options:
#        sx = sy = self.options['scale'] # FIXME
#        bx0 *= sx
#        by0 *= sy
#        bx1 *= sx
#        by1 *= sy
#        
#      if 'angle' in self.options:
#        bx0, by0, bx1, by1 = rotate_bbox((bx0, by0, bx1, by1), self.options['angle'])

#      tx, ty = self._pos
#      self._bbox = (bx0+tx, by0+ty, bx1+tx, by1+ty)
#      
#    return self._bbox

#class LineShape(BaseShape):
#  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._bbox = [x0, y0, x1, y1]
#    self.update_tags()

#class RectShape(BaseShape):
#  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._bbox = [x0, y0, x1, y1]
#    self.update_tags()


#class OvalShape(BaseShape):
#  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._bbox = [x0, y0, x1, y1]
#    self.update_tags()

#class ArcShape(BaseShape):
#  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._bbox = [x0, y0, x1, y1]
#    self.update_tags()

#  @property
#  def bbox(self):
#    lw = self.param('width')
#    if lw is None:
#      lw = 0
#      
#    lw /= 2.0

#    # Calculate bounding box for arc segment
#    x0, y0, x1, y1 = self.points
#    xc = (x0 + x1) / 2.0
#    yc = (y0 + y1) / 2.0
#    hw = abs(x1 - x0) / 2.0
#    hh = abs(y1 - y0) / 2.0

#    start = self.options['start'] % 360
#    extent = self.options['extent']
#    stop = (start + extent) % 360

#    if extent < 0:
#      start, stop = stop, start  # Swap points so we can rotate CCW

#    if stop < start:
#      stop += 360 # Make stop greater than start

#    angles = [start, stop]

#    # Find the extrema of the circle included in the arc
#    ortho = (start // 90) * 90 + 90
#    while ortho < stop:
#      angles.append(ortho)
#      ortho += 90 # Rotate CCW


#    # Convert all extrema points to cartesian
#    points = [(hw * math.cos(math.radians(a)), -hh * math.sin(math.radians(a))) for a in angles]

#    points = list(zip(*points))
#    bx0 = min(points[0]) + xc - lw
#    by0 = min(points[1]) + yc - lw
#    bx1 = max(points[0]) + xc + lw
#    by1 = max(points[1]) + yc + lw

#    #print('@@ ARC BB:', (bx0,by0,bx1,by1), hw, hh, angles, start, extent)
#    return (bx0,by0,bx1,by1)

#class PathShape(BaseShape):
#  def __init__(self, nodes, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    self.nodes = nodes
#    #self.options = options
#    #self._bbox = [x0, y0, x1, y1]
#    self.update_tags()

#  @property
#  def bbox(self):
#    extrema = []
#    for p in self.nodes:
#      if len(p) == 2:
#        extrema.append(p)
#      elif len(p) == 6: # FIXME: Compute tighter extrema of spline
#        extrema.append(p[0:2])
#        extrema.append(p[2:4])
#        extrema.append(p[4:6])
#      elif len(p) == 5: # Arc
#        extrema.append(p[0:2])
#        extrema.append(p[2:4])
#        
#    extrema = list(zip(*extrema))
#    x0 = min(extrema[0])
#    y0 = min(extrema[1])
#    x1 = max(extrema[0])
#    y1 = max(extrema[1])
#    
#    return (x0, y0, x1, y1)



#class TextShape(BaseShape):
#  text_id = 1
#  def __init__(self, x0, y0, surf, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._pos = (x0, y0)

#    if 'spacing' not in options:
#      options['spacing'] = -8
#    if 'anchor' not in options:
#      options['anchor'] = 'c'
#      
#    spacing = options['spacing']

#    bx0,by0, bx1,by1 = surf.text_bbox(options['text'], options['font'], spacing)
#    w = bx1 - bx0
#    h = by1 - by0
#    
#    self._bbox = [x0, y0, x0+w, y0+h]
#    self.move(*self.anchor_offset)
#    
#    #self._bbox = text_bbox(options['text'], options['font'])
#    self.update_tags()
#    #print('## NEW TEXT:', x0, y0, self._bbox, anchor)

#  @property
#  def anchor_offset(self):
#    x0, y0, x1, y1 = self._bbox
#    w = abs(x1 - x0)
#    h = abs(y1 - y0)
#    hw = w / 2.0
#    hh = h / 2.0

#  
#    anchor = self.param('anchor').lower()
#    spacing = self.param('spacing')
#    
#    # Decode anchor
#    anchor = anchor.replace('center','c')
#    anchor = anchor.replace('east','e')
#    anchor = anchor.replace('west','w')
#    ax = 0
#    ay = 0
#    
#    if 'n' in anchor:
#      ay = hh + (spacing // 2)
#    elif 's' in anchor:
#      ay = -hh - (spacing // 2)
#    
#    if 'e' in anchor:
#      ax = -hw
#    elif 'w' in anchor:
#      ax = hw
#      
#    # Convert from center to upper-left corner
#    return (ax - hw, ay - hh)

#  @property
#  def next_text_id(self):
#    rval = TextShape.text_id
#    TextShape.text_id += 1
#    return rval



#class DoubleRectShape(BaseShape):
#  def __init__(self, x0, y0, x1, y1, options=None, **kwargs):
#    BaseShape.__init__(self, options, **kwargs)
#    #self.options = options
#    self._bbox = [x0, y0, x1, y1]
#    self.update_tags()

#def cairo_draw_DoubleRectShape(shape, surf):
#  c = surf.ctx
#  x0, y0, x1, y1 = shape.points
#  
#  c.rectangle(x0,y0, x1-x0,y1-y0)

#  stroke = True if shape.options['width'] > 0 else False

#  #print('%% RECT:', stroke, shape.options)
#  if 'fill' in shape.options:
#    c.set_source_rgba(*rgb_to_cairo(shape.options['fill']))
#    if stroke:
#      c.fill_preserve()
#    else:
#      c.fill()

#  if stroke:
#    # FIXME c.set_source_rgba(*default_pen)
#    c.set_source_rgba(*rgb_to_cairo((100,200,100)))
#    c.stroke()
#    
#    c.rectangle(x0+4,y0+4, x1-x0-8,y1-y0-8)
#    c.stroke()


class NuCanvas(GroupShape):
  '''This is a clone of the Tk canvas subset used by the original Tcl
     It implements an abstracted canvas that can render objects to different
     backends other than just a Tk canvas widget.
  '''
  def __init__(self, surf):
    GroupShape.__init__(self, surf, 0, 0, {})
    self.markers = {}
    
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

    #print('## BBB', (bx0, by0, bx1, by1), boxes)
    return (bx0, by0, bx1, by1)

  def move(self, item, dx, dy):
    #print('## MOVE 1', item, dx, dy, 'Shapes:', len(self._get_shapes(item)))
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

  surf = CairoSurface('nc.png', DrawStyle(), padding=5)
  
  surf.add_shape_class(DoubleRectShape, cairo_draw_DoubleRectShape)
  
  nc = NuCanvas(surf)
  
  nc.create_rectangle(5,5, 20,20, fill=(255,0,0))
  nc.create_rectangle(35,2, 40,60, width=2, fill=(255,0,0))
  
  nc.create_rectangle(65,35, 150,50, width=0, fill=(255,0,0))
  nc.create_oval(65,35, 150,50, width=2, fill=(0,100,255))
  
  nc.create_shape(DoubleRectShape, 10,80, 40,140, width=3, fill=(0,255,255))
  g = nc.create_group(30,20, angle=-30, scale=2)
  g.create_rectangle(0,0,40,40, fill=(100,100,200, 150), width=3, line_color=(0,0,0))
  g.create_rectangle(0,50,40,70, fill=(100,200,100), width=3)
  
  gbb = g.bbox
  nc.create_rectangle(*gbb, width=1)

  abox = (60,60, 120,100)
  nc.create_rectangle(*abox, line_color=(10,255,10), width=4)
  arc = nc.create_arc(*abox, start=-45, extent=70, width=4, line_color=(255,0,0), fill=(0,255,0,127))
  abb = arc.bbox
  nc.create_rectangle(*abb, width=1)

  nc.create_path([(14,14), (30,4), (150,-60, 190,110, 140,110), (20,120), 'z'], fill=(255,100,0,127), width=2)
  
  nc.create_oval(50-2,80-2, 50+2,80+2, width=0, fill=(255,0,0))
  nc.create_text(50,80, text='Hello\nworld', anchor='nw', font=('Helvetica', 14, 'normal'), text_color=(0,255,0), spacing=-8)
  nc.create_text(50,100, text='Hello world', anchor='ne')

  
  nc.render()
  
