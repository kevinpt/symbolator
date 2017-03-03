#!/usr/bin/python

from __future__ import print_function

import sys, copy, re, argparse, os

from nucanvas import DrawStyle, NuCanvas
from nucanvas.cairo_backend import CairoSurface
from nucanvas.svg_backend import SvgSurface
from nucanvas.shapes import PathShape, OvalShape
from vhdl_extract import VhdlExtractor
import nucanvas.color.sinebow as sinebow

__version__ = '0.5'


def xml_escape(txt):
  txt = txt.replace('&', '&amp;')
  txt = txt.replace('<', '&lt;')
  txt = txt.replace('>', '&gt;')
  txt = txt.replace('"', '&quot;')
  return txt


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
    return re.sub(r'(\[.*\])', r'<span foreground="red">\1</span>', xml_escape(self.text))

  @property
  def styled_type(self):
    if self.data_type:
      return re.sub(r'(\[.*\])', r'<span foreground="pink">\1</span>', xml_escape(self.data_type))
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

    return g

  def text_width(self, c, font_params):
    x0, y0, x1, y1, baseline = c.surf.text_bbox(self.text, font_params)
    w = abs(x1 - x0)
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
      'clocks': sinebow.lighten(sinebow.sinebow(0), 0.75),    # Red
      'data': sinebow.lighten(sinebow.sinebow(0.35), 0.75),   # Green
      'control': sinebow.lighten(sinebow.sinebow(0.15), 0.75) # Yellow
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
  def __init__(self, component=None, symbols=None, symbol_spacing=10, width_steps=20):
    self.symbols = symbols if symbols is not None else []
    self.symbol_spacing = symbol_spacing
    self.width_steps = width_steps
    self.component = component



  def add_symbol(self, symbol):
    self.symbols.append(symbol)

  def draw(self, x, y, c):
    style = c.surf.def_styles
    sym_width = max(s.min_width(c, style.font) for sym in self.symbols for s in sym.sections)

    sym_width = (sym_width // self.width_steps + 1) * self.width_steps

    yoff = y
    for i, s in enumerate(self.symbols):
      bb = s.draw(x, y + yoff, c, sym_width)

      if i == 0 and self.component:
        # Add component name
        c.create_text((bb[0]+bb[2])/2.0,bb[1] - self.symbol_spacing, anchor='cs',
          text=self.component, font=('Helvetica', 14, 'bold'))

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
    elif pdir in ('out', 'inout'):
      side = 'r'


    pin = Pin(pname, side=side, data_type=data_type)
    if pdir == 'inout':
      pin.bidir = True

    # Check for pin name patterns
    #pname = pname.lower()

    pin_patterns = {
      'clock': re.compile(r'(^cl(oc)?k)|(cl(oc)?k$)', re.IGNORECASE),
      'bubble': re.compile(r'_n$', re.IGNORECASE),
      'bus': re.compile(r'(\[.*\]$)', re.IGNORECASE)
    }


    if pdir == 'in' and pin_patterns['clock'].search(pname):
      pin.clocked = True

    if pin_patterns['bubble'].search(pname):
      pin.bubble = True

    if bus or pin_patterns['bus'].search(pname):
      pin.bus = True

    sect.add_pin(pin)

  return sect

def make_symbol(entity_data):
  vsym = HdlSymbol(entity_data['name'])

  color_seq = sinebow.distinct_color_sequence(0.9)

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
  parser.add_argument('-L', '--library', dest='lib_path', action='store',
    default='.', help='Library path')
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


def file_search(base_dir, extensions=('.vhdl', '.vhd')):
  extensions = set(extensions)
  hdl_files = []
  for root, dirs, files in os.walk(base_dir):
    for f in files:
      if os.path.splitext(f)[1].lower() in extensions:
        hdl_files.append(os.path.join(root, f))

  return hdl_files

if __name__ == '__main__':

  args = parse_args()

  style = DrawStyle()
  style.line_color = (0,0,0)

  ve = VhdlExtractor()

  # Find all library files
  print('Scanning library:', args.lib_path)
  flist = file_search(args.lib_path)
  if os.path.isfile(args.input):
    flist.append(args.input)

  # Find all of the array types
  ve.extract_array_types(flist)

  if os.path.isfile(args.input):
    all_components = {args.input: ve.extract_components(args.input)}

  elif os.path.isdir(args.input):
    flist = file_search(args.input)
    all_components = {f: ve.extract_components(f) for f in flist}

  else:
    print('ERROR: Invalid input source')
    sys.exit(1)

  #print(all_components)
  

  nc = NuCanvas(None)

  # Set markers for all shapes
  nc.add_marker('arrow_fwd',
    PathShape(((0,-4), (2,-1, 2,1, 0,4), (8,0), 'z'), fill=(0,0,0), width=0),
    (3.2,0), 'auto', None)

  nc.add_marker('arrow_back',
    PathShape(((0,-4), (-2,-1, -2,1, 0,4), (-8,0), 'z'), fill=(0,0,0), width=0),
    (-3.2,0), 'auto', None)

  nc.add_marker('bubble',
    OvalShape(-3,-3, 3,3, fill=(255,255,255), width=1),
    (0,0), 'auto', None)

  nc.add_marker('clock',
    PathShape(((0,-7), (0,7), (7,0), 'z'), fill=(255,255,255), width=1),
    (0,0), 'auto', None)

  # Render every component from every file into an image
  for source, components in all_components.iteritems():
    for entity_data in components:
      fname = entity_data['name'] + '.' + args.output
      base = os.path.splitext(os.path.basename(source))[0]
      fname = '{}-{}.{}'.format(base, entity_data['name'], args.output)
      print('Creating symbol for {} "{}"'.format(source, entity_data['name']))
      #print('## Entity:', entity_data)
      if args.output == 'svg':
        surf = SvgSurface(fname, style, padding=5, scale=1)
      else:
        surf = CairoSurface(fname, style, padding=5, scale=1)

      nc.set_surface(surf)
      nc.clear_shapes()

      #print(entity_data)

      sym = make_symbol(entity_data)
      sym.draw(0,0, nc)

      #nc.dump_shapes()
      nc.render()


