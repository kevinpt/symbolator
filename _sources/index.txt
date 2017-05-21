
==========
Symbolator
==========

Symbolator is a component diagramming tool for VHDL and Verilog. It will parse HDL source files, extract components or modules and render them as an image.

.. code-block:: vhdl

  library ieee;
  use ieee.std_logic_1164.all;

  package demo is
    component demo_device is
      generic (
        SIZE : positive;
        RESET_ACTIVE_LEVEL : std_ulogic := '1'
      );
      port (
        --# {{clocks|}}
        Clock : in std_ulogic;
        Reset : in std_ulogic;
        
        --# {{control|Named section}}
        Enable : in std_ulogic;
        Data_in : in std_ulogic_vector(SIZE-1 downto 0);
        Data_out : out std_ulogic_vector(SIZE-1 downto 0)
      );
    end component;
  end package;


.. parsed-literal::

  > symbolator -i demo_device.vhdl
  Scanning library: .
  Creating symbol for demo_device.vhdl "demo_device"
	    -> demo_device-demo_device.svg

Produces the following:
 
.. figure:: images/demo_device-demo_device.svg
  :align: center

Symbolator can render to PNG bitmap images or SVG, PDF, PS, and EPS vector images. SVG is the default.



Requirements
------------

Symbolator requires either Python 2.7 or Python 3.x, Pycairo, and Pango.

The installation script depends on setuptools. The source is written in
Python 2.7 syntax but will convert cleanly to Python 3 when the installer
passes it through 2to3.

The Pango library is used compute the dimensions of a text layout. There is no standard package to get the Pango Python bindings installed. It is a part of the Gtk+ library which is accessed either through the PyGtk or PyGObject APIs, both of which are supported by Symbolator. You should make sure that one of these libraries is available before installing Symbolator. A `Windows installer <http://www.pygtk.org/downloads.html>`_ is available. For Linux distributions you should install the relevant libraries with your package manager.

Licensing
---------

Symbolator is licensed for free commercial and non-commercial use under the terms of the MIT license.


Download
--------

You can access the Symbolator Git repository from `Github
<https://github.com/kevinpt/symbolator>`_. You can install direct from PyPI with the "pip"
command if you have it available.


Installation
------------

Symbolator is a Python application. You must have Python installed first to use it. Most modern Linux distributions and OS/X have it available by default. There are a number of options available for Windows. If you don't already have a favorite, I recommend getting one of the `"full-stack" Python distros <http://www.scipy.org/install.html>`_ that are geared toward scientific computing such as Anaconda or Python(x,y).

If your OS has a package manager, it may be preferable to install Python setuptools through that tool before attempting to install Symbolator. Otherwise, the installation script will install these packages directly without registering them with the OS package manager.

The easiest way to install Symbolator is from `PyPI <https://pypi.python.org/pypi/symbolator>`_.

.. code-block:: sh

  > pip install --upgrade symbolator

This will download and install the latest release, upgrading if you already have it installed. If you don't have ``pip`` you may have the ``easy_install`` command available which can be used to install ``pip`` on your system:

.. code-block:: sh

  > easy_install pip


You can also use ``pip`` to get the latest development code from Github:

.. code-block:: sh

  > pip install --upgrade https://github.com/kevinpt/symbolator/tarball/master

If you manually downloaded a source package or created a clone with Git you can install Symbolator with the following command run from the base Symbolator directory:

.. code-block:: sh

  > python setup.py install

On Linux systems you may need to install with root privileges using the *sudo* command.

After a successful install the Symbolator command line application will be available. On Linux they should be immediately accessible from your current search path. On Windows you will need to make sure that the ``<Python root>\Scripts`` directory is in your %PATH% environment variable.

If you can't use the installer script, it is possible to use ``symbolator.py`` directly without installation. If you need to use Python 3 you can manually convert it with the ``2to3`` tool:

.. code-block:: sh

  > 2to3 -w symbolator.py

Command line
------------

Symbolator is a command line tool. You pass it one or more source files and it will generate symbols in any of the supported output formats.

.. parsed-literal::

  usage: symbolator [-h] [-i INPUT] [-o OUTPUT] [-f FORMAT] [-L LIB]
                    [-s SAVE_LIB] [-t] [--scale SCALE] [--title] [--verilog]
                    [-v]

  HDL symbol generator

  optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                          HDL source ("-" for STDIN)
    -o OUTPUT, --output OUTPUT
                          Output file
    -f FORMAT, --format FORMAT
                          Output format
    -L LIB_DIRS, --library LIB_DIRS
                          Library path
    -s SAVE_LIB, --save-lib SAVE_LIB
                          Save type def cache file
    -t, --transparent     Transparent background
    --scale SCALE         Scale image
    --title               Add component name above symbol
    --no-type             Omit pin type information
    -v, --version         Symbolator version


You can supply the input with the ``-i`` option in one of three forms.

* Single source file
* Source directory
* Stdin "-"

When you pass a directory, all source files will be recursively searched for VHDL and Verilog source files. When using stdin the language is detected by searching for the substring "endmodule" in which case Verilog is assumed if it is present, otherwise the VHDL parser is used. For the other input types the language is determined from the file extension.

.. parsed-literal::

  > symbolator -i foo.vhdl
  > symbolator -i bar.v
  > symbolator -i dir_name
  > symbolator -i - < foo.vhdl
  > symbolator -i - < bar.v

When input is from a file, the file name is prepended to any component/module name. This allows you to have the same component name in different source files and still keep the generated images together in a single directory.

You can provide an optional output file name or directory path with ``-o``. Any intermediate directories in the path will be created automatically.

The output format can be set with the ``-f`` option. You pass it the extension of the format you want the symbol to be generated in. It can be any of: png, svg, pdf, ps, or eps.

An optional title can be added above the symbol with the ``--title`` option. It will be the name of the component or module.

You can remove type information outside the symbol by passing the ``--no-type`` option.

Using Symbolator
----------------

The VHDL parser will only extract component declarations inside a package. Entity declarations and nested components are ignored. All Verilog modules will be extracted. Both 1995 and 2001 syntax is suported. VHDL generics and Verilog parameters are supported. They render as a separate gray block with inputs. 

.. code-block:: verilog

  module vlog_params
    (foo, bar);
    
    parameter PARAM1 = 1, PARAM2 = 2;
    
    input wire foo;
    output reg bar;
  endmodule;

.. symbolator::
  :name: param-example
  
  module vlog_params
    (foo, bar);
    
    parameter PARAM1 = 1, PARAM2 = 2;
    
    input wire foo;
    output reg bar;
  endmodule;

Special pins
~~~~~~~~~~~~

Symbol pins can have edge sensitivity triangles and inversion bubbles. They are generated when the pin name matches the following patterns:

Clocks

  "clock" or "clk" at the beginning or end of the name (``(^cl(oc)?k)|(cl(oc)?k$)``)
  
Inversion (active low)

  "_n" or "_b" at the end of the name (``_[nb]$``)
  
Bidirectional pins are rendered with double arrows. Inputs are always on the left. Outputs and bidirectional pins are on the right. Pins are kept in the same order they appear in each section.

.. code-block:: vhdl

  component example is
    port (
      Clk        : in    std_ulogic;
      Rst_n      : in    std_ulogic;
      En_b       : in    std_ulogic;
      Bidir_port : inout std_ulogic;
      Bus_port   : out   unsigned
    );
  end component;

.. symbolator::
  :name: pin-types

  component example is
    port (
      Clk        : in    std_ulogic;
      Rst_n      : in    std_ulogic;
      En_b       : in    std_ulogic;
      Bidir_port : inout std_ulogic;
      Bus_port   : out   unsigned
    );
  end component;

Busses
~~~~~~

Pins with VHDL array types will be rendered as a bus. If the range is explicitly listed it will appear in brackets separated by a ':' for descending ranges and '→' for ascending ranges.

.. code-block:: vhdl

  subtype word is unsigned(7 downto 0);

  component busses is
    port (
      Unconstrained : in signed;
      User_defined  : in word;
      Descending    : in unsigned(7 downto 0);
      Ascending     : in bit_vector(0 to 7)
    );
  end component;


.. symbolator::
  :name: bus-detect
  
  subtype word is unsigned(7 downto 0);

  component busses is
    port (
      Unconstrained : in signed;
      User_defined  : in word;
      Descending    : in unsigned(7 downto 0);
      Ascending     : in bit_vector(0 to 7)
    );
  end component;

For Verilog, any pin with a range declaration ``[...]`` will render as a bus.

Libraries
~~~~~~~~~

For VHDL, it is necessary to know which data types are array types so they can be rendered as bus pins. To accomplish this Symbolator needs to scan all library code for array type and subtype definitions. The optional ``-L`` parameter takes a path to the library directory that is recursively scanned for all VHDL source files. Built-in standard VHDL array types are automatically included. Multiple libraries can be scanned by pasing in additional ``-L`` options.

You can save scanned array definitions to a cached file with the ``-s`` option. To use this cached type listing you pass it as the argument to ``-L`` on future Symbolator invocations.

.. parsed-literal::

  > symbolator -L my/vhdl/library -L . -s libs.txt
  > symbolator -L libs.txt -i source/path

  
Symbol sections
~~~~~~~~~~~~~~~

Each symbol can be split into sections with an optional name and styling class. Sections are denoted by a metacomment starting with "--#" for VHDL or "//#" for Verilog. Following that is a label in double curly braces. For assigning a section style you prefix the label with the class name and a '|' character.

.. code-block:: vhdl

  -- Empty section:
  --# {{}}
  
  -- Styled section:
  --# {{clocks|}}
  
  -- Named section:
  --# {{Arbitrary name}}
  
  -- Styled and named:
  --# {{data|Input port}}
  
The fixed style names are "clocks", "control", and "data". They always have the same fill colors to maintain consistency across symbols. Any other sections are assigned a pastel color from a pseudo-random sequence.


.. code-block:: vhdl

  component sectioned is
    port (
      --# {{clocks|Clocking}}
      Clock : in std_ulogic;
      
      --# {{control|Control signals}}
      Enable: in std_ulogic;
      
      --# {{data|Data port}}
      Data1 : in std_ulogic;
      
      --# {{Additional port1}}
      Data2 : out std_ulogic;
      
      --# {{}}
      Data3 : inout std_ulogic
    );
  end component;


.. symbolator::
  :name: sections

  component sectioned is
    port (
      --# {{clocks|Clocking}}
      Clock : in std_ulogic;
      
      --# {{control|Control signals}}
      Enable: in std_ulogic;
      
      --# {{data|Data port}}
      Data1 : in std_ulogic;
      
      --# {{Additional port1}}
      Data2 : out std_ulogic;
      
      --# {{}}
      Data3 : inout std_ulogic
    );
  end component;


Transparency
~~~~~~~~~~~~

By default the images have a white background. If you want a transparent background pass the ``-t`` option.

Scaling
~~~~~~~

You can control the scale of the resulting image with the ``--scale`` option. It takes a floating point scale factor. This is most useful for the PNG output to increase the resolution of the image or create thumbnails with less blurring than conventional bitmap resizing.

.. parsed-literal::

  > symbolator -i scaled.vhdl --scale=0.5

.. figure:: images/scaled-scaled.svg
  :align: center



Sphinx Extension
----------------

A Symbolator extension is avaiable for the Sphinx document generation system. It adds a new "symbolator" directive that allows you to convert inline component or module declarations into an image without manually running Symbolator.

.. code-block:: rst

  .. symbolator::
  
    component foo is
      ...
    end component;

The body of the directive is the HDL code to parse into a symbol. The directive can take the following options:

alt

  Alternative text for non-graphic output

align

  Alignment (left, center, or right)

caption

  Caption text placed below the image

symbolator_cmd

  Path to the symbolator command

name

  Logical name ("id" attribute in HTML output)


Images are named by default with a SHA1 hash of the code and settings used to generate them. If the "name" option is passed it will be used to construct the file name without the hash.

.. code-block:: rst

  .. symbolator::
    :alt: Alt text
    :align: center
    :caption: Caption text
    :symbolator_cmd: /usr/local/bin/symbolator
    :name: vlog-example
  
    module vlog
      (foo, bar);
      
      input wire foo;
      output reg bar;
    endmodule;

.. symbolator::
  :alt: Alt text
  :align: center
  :caption: Caption text
  :symbolator_cmd: /usr/local/bin/symbolator
  :name: vlog-example

  module vlog
    (foo, bar);
    
    input wire foo;
    output reg bar;
  endmodule;

You can enable the Sphinx extension by adding the "symbolator_sphinx" package to your conf.py file:

.. code-block:: python

  # Add any Sphinx extension module names here, as strings. They can be
  # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
  # ones.
  extensions = ['symbolator_sphinx']

You can set configuration options in the conf.py file:

symbolator_cmd

  Set the path to the symbolator command

symbolator_cmd_args

  List of arguments to pass on each invocation of Symbolator
  
symbolator_output_format

  Change the default output format. Only PNG and SVG are supported by the Sphinx extension.


.. code-block:: python
  
  symbolator_cmd = '/usr/local/bin/symbolator'
  symbolator_cmd_args = ['-t', '--scale=0.5']
  symbolator_output_format = 'png'  # 'svg' is other format

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

