#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright © 2017 Kevin Thibedeau
# Distributed under the terms of the MIT license
from __future__ import print_function

import sys, copy, re, argparse, os, errno

from nucanvas import DrawStyle, NuCanvas
from nucanvas.cairo_backend import CairoSurface
from nucanvas.svg_backend import SvgSurface
from nucanvas.shapes import PathShape, OvalShape
import nucanvas.color.sinebow as sinebow

import hdlparse.vhdl_parser as vhdl
import hdlparse.verilog_parser as vlog


__version__ = '1.0.1'


def xml_escape(txt):
  '''Replace special characters for XML strings'''
  txt = txt.replace('&', '&amp;')
  txt = txt.replace('<', '&lt;')
  txt = txt.replace('>', '&gt;')
  txt = txt.replace('"', '&quot;')
  return txt


class Pin(object):
  '''Symbol pin'''
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
    return re.sub(r'(\[.*\])', r'<span foreground="#039BE5">\1</span>', xml_escape(self.text))

  @property
  def styled_type(self):
    if self.data_type:
      return re.sub(r'(\[.*\])', r'<span foreground="#039BE5">\1</span>', xml_escape(self.data_type))
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
  '''Symbol section'''
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

    if self.name is not None:
      x0, y0, x1, y1, baseline = c.surf.text_bbox(self.name, font_params)
      w = abs(x1 - x0)
      name_width = self.padding + w

      if lmax > 0:
        lmax = max(lmax, name_width)
      else:
        rmax = max(rmax, name_width)

    return lmax + rmax + self.padding

  def draw(self, x, y, width, c):
    dy = self.spacing

    g = c.create_group(x,y)

    toff = 0

    title_font = ('Times', 12, 'italic')
    if self.show_name and self.name is not None and len(self.name) > 0: # Compute title offset
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
  '''Symbol composed of sections'''
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
  '''Top level symbol object'''
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



def make_section(sname, sect_pins, fill, extractor, no_type=False):
  '''Create a section from a pin list'''
  sect = PinSection(sname, fill=fill)
  side = 'l'

  for p in sect_pins:
    pname = p.name
    pdir = p.mode
    data_type = p.data_type if no_type == False else None
    bus = extractor.is_array(p.data_type)

    pdir = pdir.lower()

    # Convert Verilog modes
    if pdir == 'input':
      pdir = 'in'
    if pdir == 'output':
      pdir = 'out'

    # Determine which side the pin is on
    if pdir in ('in'):
      side = 'l'
    elif pdir in ('out', 'inout'):
      side = 'r'

    pin = Pin(pname, side=side, data_type=data_type)
    if pdir == 'inout':
      pin.bidir = True

    # Check for pin name patterns
    pin_patterns = {
      'clock': re.compile(r'(^cl(oc)?k)|(cl(oc)?k$)', re.IGNORECASE),
      'bubble': re.compile(r'_[nb]$', re.IGNORECASE),
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

def make_symbol(comp, extractor, title=False, no_type=False):
  '''Create a symbol from a parsed component/module'''
  vsym = HdlSymbol() if title == False else HdlSymbol(comp.name)

  color_seq = sinebow.distinct_color_sequence(0.6)

  if len(comp.generics) > 0: #'generic' in entity_data:
    s = make_section(None, comp.generics, (200,200,200), extractor, no_type)
    s.line_color = (100,100,100)
    gsym = Symbol([s], line_color=(100,100,100))
    vsym.add_symbol(gsym)
  if len(comp.ports) > 0: #'port' in entity_data:
    psym = Symbol()

    # Break ports into sections
    cur_sect = []
    sections = []
    sect_name = comp.sections[0] if 0 in comp.sections else None
    for i,p in enumerate(comp.ports):
      if i in comp.sections and len(cur_sect) > 0: # Finish previous section
        sections.append((sect_name, cur_sect))
        cur_sect = []
        sect_name = comp.sections[i]
      cur_sect.append(p)

    if len(cur_sect) > 0:
      sections.append((sect_name, cur_sect))

    for sdata in sections:
      s = make_section(sdata[0], sdata[1], sinebow.lighten(next(color_seq), 0.75), extractor, no_type)
      psym.add_section(s)

    vsym.add_symbol(psym)

  return vsym

def parse_args():
  '''Parse command line arguments'''
  parser = argparse.ArgumentParser(description='HDL symbol generator')
  parser.add_argument('-i', '--input', dest='input', action='store', help='HDL source ("-" for STDIN)')
  parser.add_argument('-o', '--output', dest='output', action='store', help='Output file')
  parser.add_argument('-f', '--format', dest='format', action='store', default='svg', help='Output format')
  parser.add_argument('-L', '--library', dest='lib_dirs', action='append',
    default=['.'], help='Library path')
  parser.add_argument('-s', '--save-lib', dest='save_lib', action='store', help='Save type def cache file')
  parser.add_argument('-t', '--transparent', dest='transparent', action='store_true',
    default=False, help='Transparent background')
  parser.add_argument('--scale', dest='scale', action='store', default='1', help='Scale image')
  parser.add_argument('--title', dest='title', action='store_true', default=False, help='Add component name above symbol')
  parser.add_argument('--no-type', dest='no_type', action='store_true', default=False, help='Omit pin type information')
  parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help='Symbolator version')

  args, unparsed = parser.parse_known_args()

  if args.version:
    print('Symbolator {}'.format(__version__))
    sys.exit(0)

  # Allow file to be passed in without -i
  if args.input is None and len(unparsed) > 0:
    args.input = unparsed[0]

  if args.format.lower() in ('png', 'svg', 'pdf', 'ps', 'eps'):
    args.format = args.format.lower()

  if args.input == '-' and args.output is None: # Reading from stdin: must have full output file name
    print('Error: output file is required')
    sys.exit(1)

  args.scale = float(args.scale)

  # Remove duplicates
  args.lib_dirs = list(set(args.lib_dirs))

  return args


def is_verilog_code(code):
  '''Identify Verilog from stdin'''
  return re.search('endmodule', code) is not None


def file_search(base_dir, extensions=('.vhdl', '.vhd')):
  '''Recursively search for files with matching extensions'''
  extensions = set(extensions)
  hdl_files = []
  for root, dirs, files in os.walk(base_dir):
    for f in files:
      if os.path.splitext(f)[1].lower() in extensions:
        hdl_files.append(os.path.join(root, f))

  return hdl_files

def create_directories(fname):
  '''Create all parent directories in a file path'''
  try:
    os.makedirs(os.path.dirname(fname))
  except OSError as e:
    if e.errno != errno.EEXIST and e.errno != errno.ENOENT:
      raise

def reformat_array_params(vo):
  '''Convert array ranges to Verilog style'''
  for p in vo.ports:
    # Replace VHDL downto and to
    data_type = p.data_type.replace(' downto ', ':').replace(' to ', u'\u2799')
    # Convert to Verilog style array syntax
    data_type = re.sub(r'([^(]+)\((.*)\)$', r'\1[\2]', data_type)

    # Split any array segment
    pieces = data_type.split('[')
    if len(pieces) > 1:
      # Strip all white space from array portion
      data_type = '['.join([pieces[0], pieces[1].replace(' ', '')])

    p.data_type = data_type

def main():
  '''Run symbolator'''
  args = parse_args()

  style = DrawStyle()
  style.line_color = (0,0,0)

  vhdl_ex = vhdl.VhdlExtractor()
  vlog_ex = vlog.VerilogExtractor()

  if os.path.isfile(args.lib_dirs[0]):
    # This is a file containing previously parsed array type names
    vhdl_ex.load_array_types(args.lib_dirs[0])

  else: # args.lib_dirs is a path
    # Find all library files
    flist = []
    for lib in args.lib_dirs:
      print('Scanning library:', lib)
      flist.extend(file_search(lib, extensions=('.vhdl', '.vhd', '.vlog', '.v'))) # Get VHDL and Verilog files
    if args.input and os.path.isfile(args.input):
      flist.append(args.input)

    # Find all of the array types
    vhdl_ex.register_files_array_types(flist)

    #print('## ARRAYS:', vhdl_ex.array_types)

  if args.save_lib:
    print('Saving type defs to "{}".'.format(args.save_lib))
    vhdl_ex.save_array_types(args.save_lib)


  if args.input is None:
    sys.exit(0)

  if args.input == '-': # Read from stdin
    code = ''.join(list(sys.stdin))
    if is_verilog_code(code):
      all_components = {'<stdin>': [(c, vlog_ex) for c in vlog_ex.extract_modules(code)]}
    else:
      all_components = {'<stdin>': [(c, vhdl_ex) for c in vhdl_ex.extract_components(code)]}
    # Output is a named file

  elif os.path.isfile(args.input):
    if vhdl.is_vhdl(args.input):
      all_components = {args.input: [(c, vhdl_ex) for c in vhdl_ex.extract_file_components(args.input)]}
    else:
      all_components = {args.input: [(c, vlog_ex) for c in vlog_ex.extract_file_modules(args.input)]}
    # Output is a directory

  elif os.path.isdir(args.input):
    flist = set(file_search(args.input, extensions=('.vhdl', '.vhd', '.vlog', '.v')))

    # Separate file by extension
    vhdl_files = set(f for f in flist if vhdl.is_vhdl(f))
    vlog_files = flist - vhdl_files

    all_components = {f: [(c, vhdl_ex) for c in vhdl_ex.extract_file_components(f)] for f in vhdl_files}

    vlog_components = {f: [(c, vlog_ex) for c in vlog_ex.extract_file_modules(f)] for f in vlog_files}
    all_components.update(vlog_components)
    # Output is a directory

  else:
    print('ERROR: Invalid input source')
    sys.exit(1)

  if args.output:
    create_directories(args.output)

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
    for comp, extractor in components:
      reformat_array_params(comp)
      if source == '<stdin>':
        fname = args.output
      else:
        base = os.path.splitext(os.path.basename(source))[0]
        fname = '{}-{}.{}'.format(base, comp.name, args.format)
        if args.output:
          fname = os.path.join(args.output, fname)
      print('Creating symbol for {} "{}"\n\t-> {}'.format(source, comp.name, fname))
      if args.format == 'svg':
        surf = SvgSurface(fname, style, padding=5, scale=args.scale)
      else:
        surf = CairoSurface(fname, style, padding=5, scale=args.scale)

      nc.set_surface(surf)
      nc.clear_shapes()

      sym = make_symbol(comp, extractor, args.title, args.no_type)
      sym.draw(0,0, nc)

      nc.render()

if __name__ == '__main__':
  main()

