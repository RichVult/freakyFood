# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', 'src').resolve()))
sys.path.insert(0, os.path.abspath('../../project'))
print("PATH:", sys.path)  # Check if the path is correct

project = 'FreakyFood'
copyright = '%Y, David Galindo Delgado, Christian Farrell, Daniel Narewski, Marcus Regan, Tyler Herlihy, Richard Vultaggio, Max Debin'
author = 'David Galindo Delgado, Christian Farrell, Daniel Narewski, Marcus Regan, Tyler Herlihy, Richard Vultaggio, Max Debin'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.viewcode',       # Links to source code
    'sphinx.ext.napoleon',       # For Google/NumPy-style docstring
    'sphinx.ext.autodoc',        # Parses docstrings
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


# To use linux.die.net:
manpages_url = 'https://linux.die.net/man/{section}/{page}'

# HTTP requests
tls_verify = False
