#!/usr/bin/python

from __future__ import print_function

import sys, copy, re, argparse

from nucanvas import DrawStyle, NuCanvas
from nucanvas.cairo_backend import CairoSurface
from nucanvas.svg_backend import SvgSurface
from vhdl_extract import VhdlExtractor
import nucanvas.color.sinebow as sinebow

__version__ = '0.5'

class Pin(object):
  def __init__(self, text, side='l', bubble=False, clocked=False, bus=False, bidir=False, data_type=None):
    self.text = text
    self.bubble = bubble
    self.side = side
    self.clocked = clocked
    self.bus = bus
    self.bidir = bidir
    self.data_type = data_type
    
    self.pin_length = 20
    self.bubble_rad = 3
    self.padding = 10
    
  @property
  def styled_text(self):
    return re.sub(r'(\[.*\])', r'<span foreground="red">\1</span>', self.text)
    
  @property
  def styled_type(self):
    if self.data_type:
      return re.sub(r'(\[.*\])', r'<span foreground="pink">\1</span>', self.data_type)
    else:
      return None

  
  def draw(self, x, y, c):
    g = c.create_group(x,y)
    #r = self.bubble_rad
    
    if self.side == 'l':
      xs = -self.pin_length
      #bx = -r
      #xe = 2*bx if self.bubble else 0
      xe = 0
    else:
      xs = self.pin_length
      #bx = r
      #xe = 2*bx if self.bubble else 0
      xe = 0

    # Whisker for pin    
    pin_width = 3 if self.bus else 1
    ls = g.create_line(xs,0, xe,0, width=pin_width)

    if self.bidir:
      ls.options['marker_start'] = 'arrow_back'
      ls.options['marker_end'] = 'arrow_fwd'
      ls.options['marker_adjust'] = 0.8

    if self.bubble:
      #g.create_oval(bx-r,-r, bx+r, r, fill=(255,255,255))
      ls.options['marker_end'] = 'bubble'
      ls.options['marker_adjust'] = 1.0
      
    if self.clocked: # Draw triangle for clock
      ls.options['marker_end'] = 'clock'
      #ls.options['marker_adjust'] = 1.0

    if self.side == 'l':
      g.create_text(self.padding,0, anchor='w', text=self.styled_text)
      
      if self.data_type:
        g.create_text(xs-self.padding, 0, anchor='e', text=self.styled_type, text_color=(150,150,150))

    else: # Right side pin
      g.create_text(-self.padding,0, anchor='e', text=self.styled_text)
      
      if self.data_type:
        g.create_text(xs+self.padding, 0, anchor='w', text=self.styled_type, text_color=(150,150,150))
      
    g.create_group(3,4)
    
      
    return g
    
  def text_width(self, c, font_params):
    x0, y0, x1, y1, baseline = c.surf.text_bbox(self.text, font_params)
    w = abs(x1 - x0)
    print('## TW:', w)
    return self.padding + w


class PinSection(object):
  def __init__(self, name, fill=None, line_color=(0,0,0)):
    self.fill = fill
    self.line_color = line_color
    self.pins = []
    self.spacing = 20
    self.padding = 5
    self.show_name = True

    self.name = name
    self.sect_class = None

    if name is not None:  
      m = re.match(r'^(\w+)\s*\|(.*)$', name)
      if m:
        self.name = m.group(2).strip()
        self.sect_class = m.group(1).strip().lower()
        if len(self.name) == 0:
          self.name = None
        
    class_colors = {
      'clocks': (255,0,0),
      'data': (255,255,0),
      'control': (0,0,255)
    }
    
    if self.sect_class in class_colors:
      self.fill = class_colors[self.sect_class]
    
  def add_pin(self, p):
    self.pins.append(p)

  @property
  def left_pins(self):
    return [p for p in self.pins if p.side == 'l']

  @property
  def right_pins(self):
    return [p for p in self.pins if p.side == 'r']
    
  @property
  def rows(self):
    return max(len(self.left_pins), len(self.right_pins))
    
  def min_width(self, c, font_params):
    try:
      lmax = max(tw.text_width(c, font_params) for tw in self.left_pins)
    except ValueError:
      lmax = 0

    try:
      rmax = max(tw.text_width(c, font_params) for tw in self.right_pins)
    except ValueError:
      rmax = 0

    return lmax + rmax + self.padding
    
  def draw(self, x, y, width, c):
    dy = self.spacing
    
    g = c.create_group(x,y)

    toff = 0

    title_font = ('Times', 12, 'italic')
    if self.show_name and self.name is not None: # Compute title offset
      x0,y0, x1,y1, baseline = c.surf.text_bbox(self.name, title_font)
      toff = y1 - y0

    top = -dy/2 - self.padding
    bot = toff - dy/2 + self.rows*dy + self.padding
    g.create_rectangle(0,top, width,bot, fill=self.fill, line_color=self.line_color)

    if self.show_name and self.name is not None:
      g.create_text(width / 2.0,0, text=self.name, font=title_font)
    

    lp = self.left_pins
    py = 0
    for p in lp:
      p.draw(0, toff + py, g)
      py += dy

    rp = self.right_pins
    py = 0
    for p in rp:
      p.draw(0 + width, toff + py, g)
      py += dy
      
    return (g, (x, y+top, x+width, y+bot))

class Symbol(object):
  def __init__(self, sections=None, line_color=(0,0,0)):
    if sections is not None:
      self.sections = sections
    else:
      self.sections = []
    self.line_width = 3
    self.line_color = line_color
    
  def add_section(self, section):
    self.sections.append(section)
    
  def draw(self, x, y, c, sym_width=None):
    if sym_width is None:
      style = c.surf.def_styles
      sym_width = max(s.min_width(c, style.font) for s in self.sections)
    
    # Draw each section
    yoff = y
    sect_boxes = []
    for s in self.sections:
      sg, sb = s.draw(x, yoff, sym_width, c)
      bb = sg.bbox
      yoff += bb[3] - bb[1]
      sect_boxes.append(sb)
      #section.draw(50, 100 + h, sym_width, nc)

    # Find outline of all sections
    hw = self.line_width / 2.0 - 0.5
    sect_boxes = list(zip(*sect_boxes))
    x0 = min(sect_boxes[0]) + hw
    y0 = min(sect_boxes[1]) + hw
    x1 = max(sect_boxes[2]) - hw
    y1 = max(sect_boxes[3]) - hw
    
    # Add symbol outline
    c.create_rectangle(x0,y0,x1,y1, width=self.line_width, line_color=self.line_color)
    
    return (x0,y0, x1,y1)

class HdlSymbol(object):
  def __init__(self, symbols=None, symbol_spacing=10, width_steps=20):
    self.symbols = symbols if symbols is not None else []
    self.symbol_spacing = symbol_spacing
    self.width_steps = width_steps

  def add_symbol(self, symbol):
    self.symbols.append(symbol)
    
  def draw(self, x, y, c):
    style = c.surf.def_styles
    sym_width = max(s.min_width(c, style.font) for sym in self.symbols for s in sym.sections)
    
    sym_width = (sym_width // self.width_steps + 1) * self.width_steps
  
    yoff = y
    for s in self.symbols:
      bb = s.draw(x, y + yoff, c, sym_width)
      
      yoff += bb[3] - bb[1] + self.symbol_spacing



def make_section(sname, sect_pins, fill):
  sect = PinSection(sname, fill=fill)
  side = 'l'

  #print('## SP:', sect_pins)
  for p in sect_pins:
    pname = p['name']
    #pdir = 'in' if len(p) < 2 else p[1]
    pdir = p['dir'] if 'dir' in p else 'in'
    #data_type = None if len(p) < 3 else p[2]
    data_type = p['type'] if 'type' in p else None
    bus = p['bus'] if 'bus' in p else False
      
    pdir = pdir.lower()
      
    if pdir == 'in':
      side = 'l'
    elif pdir == 'out':
      side = 'r'

    
    pin = Pin(pname, side=side, data_type=data_type)
    if pdir == 'inout':
      pin.bidir = True

    # Check for pin name patterns
    pname = pname.lower()

    # FIXME: abstract these
    if pname.endswith('clock') or pname.endswith('clk') or \
        pname.startswith('clock') or pname.startswith('clk'):
      pin.clocked = True
      
    if pname.endswith('_n'):
      pin.bubble = True
      
    if re.search(r'(\[.*\]$)', pname) or bus:
      pin.bus = True

    sect.add_pin(pin)
    
  return sect

def make_symbol(entity_data):
  vsym = HdlSymbol()
  
  color_seq = sinebow.distinct_color_sequence()
  
  #print('## edata:', entity_data['port'])
  
  if 'generic' in entity_data:
    s = make_section(None, entity_data['generic'], (200,200,200))
    s.line_color = (100,100,100)
    gsym = Symbol([s], line_color=(100,100,100))
    vsym.add_symbol(gsym)
  if 'port' in entity_data:
    psym = Symbol()
    for sdata in entity_data['port']:
      #print('## SDAT:', sdata[0])
      s = make_section(sdata[0], sdata[1], sinebow.lighten(next(color_seq), 0.75))
      psym.add_section(s)
    
    vsym.add_symbol(psym)
    
  return vsym
  
def parse_args():
  parser = argparse.ArgumentParser(description='HDL symbol generator')
  parser.add_argument('-i', '--input', dest='input', action='store', help='HDL source')
  parser.add_argument('-o', '--output', dest='output', action='store', help='Output format')
  parser.add_argument('-t', '--transparent', dest='transparent', action='store_true',
    default=False, help='Transparent background')
  parser.add_argument('--scale', dest='scale', action='store', default='1', help='Scale image')
  parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help='Syntrax version')

  args, unparsed = parser.parse_known_args()
  
  if args.version:
    print('Symbolator {}'.format(__version__))
    sys.exit(0)

  # Allow file to be passed in without -i
  if args.input is None and len(unparsed) > 0:
    args.input = unparsed[0]

  if args.input is None:
    print('Error: input file is required')
    sys.exit(1)
    
  if args.output is None: # Default to png
    args.output = 'png'

  if args.output.lower() in ('png', 'svg', 'pdf', 'ps', 'eps'):
    args.output = args.output.lower()

  args.scale = float(args.scale)
  
  return args


if __name__ == '__main__':

  args = parse_args()

  style = DrawStyle()
  style.line_color = (0,0,0)

  ve = VhdlExtractor(set(('reg_word', 'reg_array')))
  components = ve.extract_components(args.input)
  
  for entity_data in components:
    fname = entity_data['name'] + '.' + args.output
    print('Creating symbol for "{}"'.format(entity_data['name']))
    if args.output == 'svg':
      surf = SvgSurface(fname, style, padding=5, scale=1)
    else:
      surf = CairoSurface(fname, style, padding=5, scale=1)

    nc = NuCanvas(surf)
    
    #print(entity_data)
    
    sym = make_symbol(entity_data)
    sym.draw(0,0, nc)
    nc.render()
  
  #surf.draw_bbox = True
  
##  surf.add_shape_class(DoubleRectShape, cairo_draw_DoubleRectShape)
#  
#  nc = NuCanvas(surf)
#  
#  nc.add_marker('arrow_fwd',
#    PathShape(((0,-4), (2,-1, 2,1, 0,4), (8,0), 'z'), fill=(0,0,0), width=0),
#    (3.2,0), 'auto', None)
#    
#  nc.add_marker('arrow_back',
#    PathShape(((0,-4), (-2,-1, -2,1, 0,4), (-8,0), 'z'), fill=(0,0,0), width=0),
#    (-3.2,0), 'auto', None)

#  nc.add_marker('bubble',
#    OvalShape(-3,-3, 3,3, fill=(255,255,255), width=1),
#    (0,0), 'auto', None)

#  nc.add_marker('clock',
#    PathShape(((0,-7), (0,7), (7,0), 'z'), fill=(255,255,255), width=1),
#    (0,0), 'auto', None)

#  
#  section = PinSection('Timing', fill=(200,150,200))
#  section.add_pin(Pin('Clock', clocked=True))
#  section.add_pin(Pin('Reset', bidir=True))
#  section.add_pin(Pin('Data[7:0]', bus=True, bubble=True))
#  section.add_pin(Pin('ClockM', side='r', clocked=True))
#  section.add_pin(Pin('Data[7:0]', bus=True, side='r', bidir=True))
#  section.add_pin(Pin('Data[7:0]', side='r', bidir=True))
#  #section.add_pin(Pin('Hello world', side='r'))
#  
#  section2 = copy.deepcopy(section)
#  section2.name = 'Control'
#  section2.fill = (230,210,200)
#  
#  #section2.add_pin(Pin('Really long pin'))
#  
#  sym = Symbol([section, section2])
#  
#  gsect = PinSection('Generic', fill=(200,200,200), line_color=(100,100,100))
#  gsect.add_pin(Pin('SIZE'))
#  gsect.add_pin(Pin('DATA_BUS'))
#  gsym = Symbol([gsect], line_color=(100,100,100))
#  
#  vsym = HdlSymbol([gsym, sym])
#  
#  #vsym.draw(0,0, nc)
#  
#  
#  entity_data = {
#    'name': 'my_entity',
#    'generic': [
#      ('G_FOO',),
#      ('G_BAR',)
#    ],
#    'port': [
#      ['Control', [
#      ('Clock', 'in', 'std_ulogic'),
#      ('Reset_N', 'in', 'std_ulogic'),
#      ('Data[G_FOO:0]', 'inout', 'std_ulogic_vector[G_FOO:0]',)
#      ]],
#      [None, [
#      ('Clock2', 'in'),
#      ('Reset2', 'in'),
#      ('Data[31:-5]', 'out'),
#      (u'DataX[0\u27994]', 'inout')
#      ]],
#      [None, [
#      ('Clock2', 'in'),
#      ('Reset2', 'in'),
#      ('Data[31:-5]', 'out'),
#      (u'DataX[0\u27994]', 'inout')
#      ]]
#    ]
#  }
  
    
  #nc.ungroup_all()

#  nc.create_text(0,0, anchor='nw', text='Data[7:0]MMM', font=('Times', 14, 'normal'))

  #nc.create_rectangle(-10,-10, 400, 400)

  #nc.create_path(((0,0), (10,10), (300, 20, 200, 200, 30), (200, 200), (40,300), 'z'))
#  nc.create_path(((0,0), (10,10), (150,80, 300,10, 30), (300,10, 220,200, 30), (220, 200), (40,300), 'z'))
#  
#  nc.create_line(100,300, 150,310, arrow='last', width=4)
#  
#  nc.add_marker('box', RectShape(0,0, 2,2, options={'fill':(255,0,0), 'width':0}),
#    (1,1), 'auto')

#  nc.add_marker('arrow2', PathShape(((0,0), (0,2), (2,0), (0,-2)), fill=(255,0,0,127), width=0),
#    (0.8,0), 'auto')

#  nc.add_marker('arrow_fwd',
#    PathShape(((0,-1), (0.5,-1, 0.5,1, 0,1), (2,0), 'z'), fill=(0,0,0), width=0),
#    (0.8,0), 'auto')

#  nc.add_marker('arrow_back',
#    PathShape(((0,-1), (-0.5,-1, -0.5,1, 0,1), (-2,0), 'z'), fill=(0,0,0), width=0),
#    (-0.8,0), 'auto')

#  
#  nc.create_line(100,200, 150,210, marker_start='arrow_back', marker_end='arrow_fwd', marker_mid='box', width=2)
 
