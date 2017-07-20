# -*- coding: utf-8 -*-
"""
    symbolator_sphinx
    ~~~~~~~~~~~~~~~~~

    Allow symbolator-formatted graphs to be included in Sphinx-generated
    documents inline.
    
    Derived from sphinx.ext.graphviz.

    :copyright: Copyright 2007-2017 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE.Sphinx for details.
"""

import re
import codecs
import posixpath
from os import path
from subprocess import Popen, PIPE
from hashlib import sha1

from six import text_type

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

import sphinx
from sphinx.errors import SphinxError
from sphinx.locale import _
#XXX from sphinx.util import logging
#XXX from sphinx.util.i18n import search_image_for_language
from sphinx.util.osutil import ensuredir, ENOENT, EPIPE, EINVAL

if False:
    # For type annotation
    from typing import Any, Dict, List, Tuple  # NOQA
    from sphinx.application import Sphinx  # NOQA

#XXX logger = logging.getLogger(__name__)


class SymbolatorError(SphinxError):
    category = 'Symbolator error'


class symbolator(nodes.General, nodes.Inline, nodes.Element):
    '''Base class for symbolator node'''
    pass


def figure_wrapper(directive, node, caption):
    # type: (Directive, nodes.Node, unicode) -> nodes.figure
    figure_node = nodes.figure('', node)
    if 'align' in node:
        figure_node['align'] = node.attributes.pop('align')

    parsed = nodes.Element()
    directive.state.nested_parse(ViewList([caption], source=''),
                                 directive.content_offset, parsed)
    caption_node = nodes.caption(parsed[0].rawsource, '',
                                 *parsed[0].children)
    caption_node.source = parsed[0].source
    caption_node.line = parsed[0].line
    figure_node += caption_node
    return figure_node


def align_spec(argument):
    # type: (Any) -> bool
    return directives.choice(argument, ('left', 'center', 'right'))


class Symbolator(Directive):
    """
    Directive to insert HDL symbol.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'caption': directives.unchanged,
        'symbolator_cmd': directives.unchanged,
        'name': directives.unchanged,
    }

    def run(self):
        # type: () -> List[nodes.Node]
        if self.arguments:
            document = self.state.document
            if self.content:
                return [document.reporter.warning(
                    'Symbolator directive cannot have both content and '
                    'a filename argument', line=self.lineno)]
            env = self.state.document.settings.env
            #XXX argument = search_image_for_language(self.arguments[0], env)
            #XXX rel_filename, filename = env.relfn2path(argument)
            rel_filename, filename = env.relfn2path(self.arguments[0])
            env.note_dependency(rel_filename)
            try:
                with codecs.open(filename, 'r', 'utf-8') as fp:
                    symbolator_code = fp.read()
            except (IOError, OSError):
                return [document.reporter.warning(
                    'External Symbolator file %r not found or reading '
                    'it failed' % filename, line=self.lineno)]
        else:
            symbolator_code = '\n'.join(self.content)
            if not symbolator_code.strip():
                return [self.state_machine.reporter.warning(
                    'Ignoring "symbolator" directive without content.',
                    line=self.lineno)]
        node = symbolator()
        node['code'] = symbolator_code
        node['options'] = {}
        if 'symbolator_cmd' in self.options:
            node['options']['symbolator_cmd'] = self.options['symbolator_cmd']
        if 'alt' in self.options:
            node['alt'] = self.options['alt']
        if 'align' in self.options:
            node['align'] = self.options['align']
            
        if 'name' in self.options:
          node['options']['name'] = self.options['name']

        caption = self.options.get('caption')
        if caption:
            node = figure_wrapper(self, node, caption)

        self.add_name(node)
        return [node]



def render_symbol(self, code, options, format, prefix='symbol'):
    # type: (nodes.NodeVisitor, unicode, Dict, unicode, unicode) -> Tuple[unicode, unicode]
    """Render symbolator code into a PNG or SVG output file."""

    symbolator_cmd = options.get('symbolator_cmd', self.builder.config.symbolator_cmd)
    hashkey = (code + str(options) + str(symbolator_cmd) +
               str(self.builder.config.symbolator_cmd_args)).encode('utf-8')

    # Use name option if present otherwise fallback onto SHA-1 hash
    name = options.get('name', sha1(hashkey).hexdigest())
    fname = '%s-%s.%s' % (prefix, name, format)
    relfn = posixpath.join(self.builder.imgpath, fname)
    #XXX outfn = path.join(self.builder.outdir, self.builder.imagedir, fname)
    outfn = path.join(self.builder.outdir, '_images', fname)

    if path.isfile(outfn):
        return relfn, outfn

    if (hasattr(self.builder, '_symbolator_warned_cmd') and
       self.builder._symbolator_warned_cmd.get(symbolator_cmd)):
        return None, None

    ensuredir(path.dirname(outfn))

    # Symbolator expects UTF-8 by default
    if isinstance(code, text_type):
        code = code.encode('utf-8')

    cmd_args = [symbolator_cmd]
    cmd_args.extend(self.builder.config.symbolator_cmd_args)
    cmd_args.extend(['-i', '-', '-f', format, '-o', outfn])
    
    try:
        p = Popen(cmd_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        #XXX logger.warning('symbolator command %r cannot be run (needed for symbolator '
        #XXX                'output), check the symbolator_cmd setting', symbolator_cmd)
        self.builder.warn('symbolator command %r cannot be run (needed for symbolator '
                          'output), check the symbolator_cmd setting' % symbolator_cmd) 
        if not hasattr(self.builder, '_symbolator_warned_cmd'):
            self.builder._symbolator_warned_cmd = {}
        self.builder._symbolator_warned_cmd[symbolator_cmd] = True
        return None, None
    try:
        # Symbolator may close standard input when an error occurs,
        # resulting in a broken pipe on communicate()
        stdout, stderr = p.communicate(code)
    except (OSError, IOError) as err:
        if err.errno not in (EPIPE, EINVAL):
            raise
        # in this case, read the standard output and standard error streams
        # directly, to get the error message(s)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        p.wait()
    if p.returncode != 0:
        raise SymbolatorError('symbolator exited with error:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    if not path.isfile(outfn):
        raise SymbolatorError('symbolator did not produce an output file:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    return relfn, outfn


def render_symbol_html(self, node, code, options, prefix='symbol',
                    imgcls=None, alt=None):
    # type: (nodes.NodeVisitor, symbolator, unicode, Dict, unicode, unicode, unicode) -> Tuple[unicode, unicode]  # NOQA
    format = self.builder.config.symbolator_output_format
    try:
        if format not in ('png', 'svg'):
            raise SymbolatorError("symbolator_output_format must be one of 'png', "
                                "'svg', but is %r" % format)
        fname, outfn = render_symbol(self, code, options, format, prefix)
    except SymbolatorError as exc:
        #XXX logger.warning('symbolator code %r: ' % code + str(exc))
        self.builder.warn('symbolator code %r: ' % code + str(exc))
        raise nodes.SkipNode

    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get('alt', self.encode(code).strip())
        imgcss = imgcls and 'class="%s"' % imgcls or ''
        if format == 'svg':
            svgtag = '''<object data="%s" type="image/svg+xml">
            <p class="warning">%s</p></object>\n''' % (fname, alt)
            self.body.append(svgtag)
        else:
            if 'align' in node:
                self.body.append('<div align="%s" class="align-%s">' %
                                 (node['align'], node['align']))
            self.body.append('<img src="%s" alt="%s" %s/>\n' %
                             (fname, alt, imgcss))
            if 'align' in node:
                self.body.append('</div>\n')

    raise nodes.SkipNode


def html_visit_symbolator(self, node):
    # type: (nodes.NodeVisitor, symbolator) -> None
    render_symbol_html(self, node, node['code'], node['options'])


def render_symbol_latex(self, node, code, options, prefix='symbol'):
    # type: (nodes.NodeVisitor, symbolator, unicode, Dict, unicode) -> None
    try:
        fname, outfn = render_symbol(self, code, options, 'pdf', prefix)
    except SymbolatorError as exc:
        #XXX logger.warning('symbolator code %r: ' % code + str(exc))
        self.builder.warn('symbolator code %r: ' % code + str(exc))
        raise nodes.SkipNode

    is_inline = self.is_inline(node)
    if is_inline:
        para_separator = ''
    else:
        para_separator = '\n'

    if fname is not None:
        post = None  # type: unicode
        if not is_inline and 'align' in node:
            if node['align'] == 'left':
                self.body.append('{')
                post = '\\hspace*{\\fill}}'
            elif node['align'] == 'right':
                self.body.append('{\\hspace*{\\fill}')
                post = '}'
        self.body.append('%s\\includegraphics{%s}%s' %
                         (para_separator, fname, para_separator))
        if post:
            self.body.append(post)

    raise nodes.SkipNode


def latex_visit_symbolator(self, node):
    # type: (nodes.NodeVisitor, symbolator) -> None
    render_symbol_latex(self, node, node['code'], node['options'])


def render_symbol_texinfo(self, node, code, options, prefix='symbol'):
    # type: (nodes.NodeVisitor, symbolator, unicode, Dict, unicode) -> None
    try:
        fname, outfn = render_symbol(self, code, options, 'png', prefix)
    except SymbolatorError as exc:
        #XXX logger.warning('symbolator code %r: ' % code + str(exc))
        self.builder.warn('symbolator code %r: ' % code + str(exc))
        raise nodes.SkipNode
    if fname is not None:
        self.body.append('@image{%s,,,[symbolator],png}\n' % fname[:-4])
    raise nodes.SkipNode


def texinfo_visit_symbolator(self, node):
    # type: (nodes.NodeVisitor, symbolator) -> None
    render_symbol_texinfo(self, node, node['code'], node['options'])


def text_visit_symbolator(self, node):
    # type: (nodes.NodeVisitor, symbolator) -> None
    if 'alt' in node.attributes:
        self.add_text(_('[symbol: %s]') % node['alt'])
    else:
        self.add_text(_('[symbol]'))
    raise nodes.SkipNode


def man_visit_symbolator(self, node):
    # type: (nodes.NodeVisitor, symbolator) -> None
    if 'alt' in node.attributes:
        self.body.append(_('[symbol: %s]') % node['alt'])
    else:
        self.body.append(_('[symbol]'))
    raise nodes.SkipNode


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]
    app.add_node(symbolator,
                 html=(html_visit_symbolator, None),
                 latex=(latex_visit_symbolator, None),
                 texinfo=(texinfo_visit_symbolator, None),
                 text=(text_visit_symbolator, None),
                 man=(man_visit_symbolator, None))
    app.add_directive('symbolator', Symbolator)
    app.add_config_value('symbolator_cmd', 'symbolator', 'html')
    app.add_config_value('symbolator_cmd_args', ['-t'], 'html')
    app.add_config_value('symbolator_output_format', 'svg', 'html')
    return {'version': '1.0', 'parallel_read_safe': True}

