# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FreakyFood'
copyright = '%Y, David Galindo Delgado, Christian Farrell, Daniel Narewski, Marcus Regan, Tyler Herlihy, Richard Vultaggio, Max Debin'
author = 'David Galindo Delgado, Christian Farrell, Daniel Narewski, Marcus Regan, Tyler Herlihy, Richard Vultaggio, Max Debin'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# To use linux.die.net:
manpages_url = 'https://linux.die.net/man/{section}/{page}'

# HTTP requests
tls_verify = False