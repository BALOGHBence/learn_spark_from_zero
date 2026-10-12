# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'my_project'
copyright = '2026, Bence Balogh'
author = 'Bence Balogh'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "nbsphinx",
    "sphinx_copybutton",
]

templates_path = ['_templates']
exclude_patterns = ["_build", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# -- Options for nbsphinx -------------------------------------------------
# https://nbsphinx.readthedocs.io/en/0.9.8/

nbsphinx_allow_errors = True
nbsphinx_execute = 'never'

# -- Options for copybutton -------------------------------------------------
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html

# Strip input prompts from copied code
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# By default, the copy button copies all the text in a code cell, including prompts. 
# Setting this to False will make it copy only the code, without the prompts.
copybutton_only_copy_prompt_lines = False