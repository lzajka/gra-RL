# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Implementacja gry wykorzystującej uczenie ze wzmocnieniem'
copyright = '2025, Łukasz Czajka'
author = 'Łukasz Czajka'
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinxcontrib.plantuml',
    'nbsphinx',
    'autoapi.extension'
]

autoapi_dirs = ['../src']
autoapi_type = "python"
autoapi_keep_files = True


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_venv']
#autoapi_ignore = ['design']
plantuml_output_format = 'svg_img'
plantuml_latex_output_format = 'tikz'
language = 'pl'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
