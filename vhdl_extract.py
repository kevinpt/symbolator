from __future__ import print_function
import io
import re


class VhdlExtractor(object):
  def __init__(self, array_types=set()):
    self.array_types = set(('std_ulogic_vector', 'std_logic_vector',
      'signed', 'unsigned', 'bit_vector'))

    self.array_types |= array_types

  def extract_components(self, fname):
    with io.open(fname, encoding='latin-1') as fh:
      lines = fh.readlines()

    comps = []
    cur_comp = []
    in_comp = False
    for l in lines:
      if re.search(r'^\s*component', l, re.IGNORECASE):
        in_comp = True

      if in_comp:
        cur_comp.append(l)

      if re.search(r'^\s*end(\s+component)*;', l, re.IGNORECASE):
        if in_comp:
          comps.append(cur_comp)
          cur_comp = []
        in_comp = False

    return [self.parse_component(c) for c in comps]


  def parse_component(self, comp):
    cname = None
    # Get the name
    m = re.search(r'component\s*([\w]+)', comp[0], re.IGNORECASE)
    if m:
      cname = m.group(1)
      #print('Name:', cname)

    if cname is None:
      return None

    in_generic = False
    in_port = False
    glines = []
    plines = []
    # Look for any generic
    for l in comp:
      if re.search(r'generic\s*\(', l, re.IGNORECASE):
        in_generic = True

      if re.search(r'port\s*\(', l, re.IGNORECASE):
        in_generic = False
        in_port = True

      if in_generic:
        glines.append(l)

      if in_port:
        plines.append(l)

    g_sect = self.parse_generic(glines)
    p_sect = self.parse_port(plines)

    cdata = {
      'name': cname,
    }

    if len(g_sect) > 0:
      cdata['generic'] = g_sect
    if len(p_sect) > 0:
      cdata['port'] = p_sect

    return cdata


  def parse_generic(self, glines):
    signals = []
    for l in glines:
      m = re.search(r'^\s*(\w+)\s*:\s*(\w+)', l)
      if m:
        pin_type = m.group(2)
        bus = True if pin_type.lower() in self.array_types else False
        pin_def = {'name': m.group(1), 'dir':'in', 'type':pin_type, 'bus':bus}
        signals.append(pin_def)
        #signals.append((m.group(1), 'in', m.group(2)))

    return signals

  def parse_port(self, plines):
    sects = []
    signals = []
    sect_name = None
    for l in plines:
      m = re.search(r'--.*{{(.*)}}', l)
      if m:
        if len(signals) > 0: # Save previous section
          sects.append([sect_name, signals])
          signals = []

        sect_name = m.group(1).strip()
        if len(sect_name) == 0:
          sect_name = None

      # Match on "name : dir type"
      m = re.search(r'^\s*(\w+)\s*:\s*(\w+)\s+(\w+)\s*(\([^)]+\))?', l)
      if m:
        pin_type = m.group(3)
        bus = True if pin_type.lower() in self.array_types else False

        pin_range = m.group(4)
        if pin_range: # Reformat it and append to the type
          pin_range = pin_range[1:-1]
          pin_range = pin_range.replace('downto', ':').replace('to', u'\u2799').replace(' ', '')
          pin_type = '{}[{}]'.format(pin_type, pin_range)

        #print('## RANGE:', pin_range)
        pin_def = {'name': m.group(1), 'dir':m.group(2), 'type':pin_type, 'bus':bus}
        signals.append(pin_def)
        #signals.append((m.group(1), m.group(2), m.group(3)))

    if len(signals) > 0: # Save previous section
      sects.append([sect_name, signals])

    return sects


    #print(lines)

  def extract_array_types(self, files):
    subtypes = {}
    for fname in files:
      with io.open(fname, encoding='latin-1') as fh:
        for l in fh:
          m = re.match(r'\s*type\s+(\w+)\s+is\s+array',l, re.IGNORECASE)
          if m:
            self.array_types.add(m.group(1))
          m = re.match(r'\s*subtype\s+(\w+)\s+is\s+(\w+)', l, re.IGNORECASE)
          if m:
            subtypes[m.group(1)] = m.group(2)

    # Find all subtypes of an array type
    for k,v in subtypes.iteritems():
      while v in subtypes: # Follow subtypes of subtypes
        v = subtypes[v]
      if v in self.array_types:
        self.array_types.add(k)

    #print('## VECTORS:', self.array_types)


if __name__ == '__main__':
  comps = extract_components('reg_file.vhdl')
  for c in comps:
    #cdata = parse_component(c)
    print(c)
