from __future__ import print_function

import re

class MiniLexer(object):

  def __init__(self, tokens, flags=re.MULTILINE):
    self.tokens = {}
    
    # Pre-process the state definitions
    for state, patterns in tokens.iteritems():
      full_patterns = []
      for p in patterns:
        pat = re.compile(p[0], flags)
        action = p[1]
        new_state = p[2] if len(p) >= 3 else None
        
        if new_state and new_state.startswith('#pop'):
          try:
            new_state = -int(new_state.split(':')[1])
          except IndexError, ValueError:
            new_state = -1
        
        full_patterns.append((pat, action, new_state))
      self.tokens[state] = full_patterns
  
  
  def run(self, text):
    stack = ['root']
    pos = 0
    
    patterns = self.tokens[stack[-1]]
    
    while True:
      #print('## pos', pos, text[pos:pos+20])
      for pat, action, new_state in patterns:
        m = pat.match(text, pos)
        if m:
          if action:
            #print('## MATCH: {} -> {}'.format(m.group(), action))
            yield pos, action, m.groups()
          
          #print('## update pos', m.end())
          pos = m.end()
          
          if new_state:
            if isinstance(new_state, int): # Pop states
              del stack[new_state:]
            else:
              stack.append(new_state)

            #print('## CHANGE STATE:', pos, new_state, stack)
            patterns = self.tokens[stack[-1]]

          break
          
      else:
        try:
          if text[pos] == '\n':
            pos += 1
            continue
          pos += 1
        except IndexError:
          break

