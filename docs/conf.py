# -*- coding: utf-8 -*-
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import subprocess
import sys
import xarray
import datetime

from contextlib import suppress
allowed_failures = set()

if 'conda' in sys.executable:
    print('conda environment:')
    subprocess.run(['conda', 'list'])
else:
    print('pip environment:')
    subprocess.run(['pip', 'list'])

print("xarray: %s, %s" % (xarray.__version__, xarray.__file__))

with suppress(ImportError):
    import matplotlib
    matplotlib.use('Agg')

autodoc_mock_imports = []
try:
    import cartopy
except ImportError:
    autodoc_mock_imports.append('cartopy')

# import pkg_resources
# __version__ = pkg_resources.get_distribution("argopy").version

argopy_src = os.path.abspath('..')
print("argopy loaded:", os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('..'))
import argopy
print("argopy: %s, %s" % (argopy.__version__, argopy.__file__))

print("python exec:", sys.executable)
print("sys.path:", sys.path)

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# extensions = ['sphinx.ext.autodoc',
#     'sphinx.ext.doctest',
#     'sphinx.ext.todo',
#     'sphinx.ext.coverage',
#     'sphinx.ext.mathjax',
#     'sphinx.ext.ifconfig',
#     'sphinx.ext.viewcode',
#     'sphinx.ext.githubpages']

extensions = [
    # 'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.inheritance_diagram',
    'matplotlib.sphinxext.plot_directive',
    'nbsphinx',
    'numpydoc',
    'sphinx_issues'
]

# sphinx_gallery_conf = {
#                        'expected_failing_examples': list(allowed_failures)
#                        }

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'argopy'
copyright = "2020-%s, argopy Developers" % datetime.datetime.now().year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ".".join(argopy.__version__.split(".")[:2])
# The full version, including alpha/beta/rc tags.
release = argopy.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
# language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_templates',
                    '.ipynb_checkpoints', '_ext', 'tempo_out', '_src',
                    'offline']

# Give *lots* of time for cell execution!
# Note nbsphinx compiles *all* notebooks in docs unless excluded
nbsphinx_timeout = 300

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'none'

# Create local pygments copies
# Previously used: https://github.com/richleland/pygments-css
# But do not want to depend on some random repository
from pygments.formatters import HtmlFormatter  # noqa: E402
from pygments.styles import get_all_styles  # noqa: E402
path = os.path.join('_static', 'pygments')
if not os.path.isdir(path):
    os.mkdir(path)
for style in get_all_styles():
    path = os.path.join('_static', 'pygments', style + '.css')
    if os.path.isfile(path):
        continue
    with open(path, 'w') as f:
        f.write(HtmlFormatter(style=style).get_style_defs('.highlight'))

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

autosummary_generate = True
numpydoc_class_members_toctree = True
numpydoc_show_class_members = False

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

extlinks = {
    'issue': ('https://github.com/euroargodev/argopy/issues/%s', 'GH#'),
    'commit': ('https://github.com/euroargodev/argopy/commit/%s', '@'),
    'pr': ('https://github.com/euroargodev/argopy/pull/%s', 'PR#'),
}

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
# html_theme = 'bootstrap'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/argopy_logo_long.png"
html_favicon = '_static/argopy.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {
    # 'canonical_url': '',
    'analytics_id': 'UA-73130866-2',  #  Provided by Google in your dashboard
    'logo_only': True,
    'display_version': False,
    'prev_next_buttons_location': 'bottom',
    # 'style_external_links': False,
    # 'vcs_pageview_mode': '',
    # 'style_nav_header_background': 'white',
    # # Toc options
    'collapse_navigation': True,
    # 'sticky_navigation': True,
    'navigation_depth': 4,
    # 'includehidden': True,
    # 'titles_only': False
}

# Sometimes the savefig directory doesn't exist and needs to be created
# https://github.com/ipython/ipython/issues/8733
# becomes obsolete when we can pin ipython>=5.2; see doc/environment.yml
ipython_savefig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '_build', 'html', '_static')
if not os.path.exists(ipython_savefig_dir):
    os.makedirs(ipython_savefig_dir)

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'argopydoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'argopy.tex', u'argopy Documentation',
     u'argopy Developers', 'manual'),
]

# -- Options for Github ---------------------------------------
# GitHub repo
issues_github_path = "euroargodev/argopy"

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'argopy', u'argopy Documentation',
     ["argopy Developers"], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'argopy', u'argopy Documentation',
     "argopy Developers", 'argopy', 'A python library for Argo data beginners and experts',
     'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'iris': ('http://scitools.org.uk/iris/docs/latest/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'numba': ('https://numba.pydata.org/numba-doc/latest/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'xarray': ('http://xarray.pydata.org/en/stable/', None),
    'dask': ('https://docs.dask.org/en/latest/', None),
    'dask_ml': ('https://ml.dask.org/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'seaborn': ('https://seaborn.pydata.org/', None),
}