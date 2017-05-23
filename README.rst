.. image:: http://kevinpt.github.io/symbolator/_static/symbolator_icon.png

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
 
.. image:: http://kevinpt.github.io/symbolator/_images/demo_device-demo_device.svg


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

Symbolator is licensed for free commercial and non-commercial use under the terms of the MIT license. The Symbolator Sphinx extension is derived from the Graphviz extension and is BSD licensed.


Download
--------

You can access the Symbolator Git repository from `Github
<https://github.com/kevinpt/symbolator>`_. You can install direct from PyPI with the "pip"
command if you have it available.

Documentation
-------------

The full documentation is available online at the `main Symbolator site
<http://kevinpt.github.io/symbolator/>`_.


