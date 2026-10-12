# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Learn Spark from Zero'
copyright = '2026, Bence Balogh'
author = 'Bence Balogh'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_copybutton",
    "myst_nb",
    "sphinx_design",
    'sphinxcontrib.mermaid',
]

templates_path = ['_templates']
exclude_patterns = ["_build", ".DS_Store"]

# Skip empty placeholder pages (e.g. a chapter scaffolded before it is
# written). An empty .ipynb is not valid JSON and would crash the build.
from pathlib import Path

_source_dir = Path(__file__).parent
exclude_patterns += [
    path.relative_to(_source_dir).as_posix()
    for pattern in ("*.md", "*.ipynb")
    for path in _source_dir.rglob(pattern)
    if path.stat().st_size == 0
]

# -- Options for MyST parser -------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html

myst_enable_extensions = [
    "dollarmath",   # $...$ and $$...$$ math
    "amsmath",      # LaTeX amsmath environments (align, etc.)
    "colon_fence",  # ::: fences for directives (used by sphinx_design)
]

# Number equations continuously across the whole project (toctree order)
# instead of restarting at (1) on every page.
numfig = True
math_numfig = True
numfig_secnum_depth = 0

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_css_files = ['css/custom.css']

# Show the in-page table of contents ("On this page") in the secondary sidebar.
html_theme_options = {
    "show_toc_level": 2,
    "secondary_sidebar_items": ["page-toc"],
    # A short navbar brand so it doesn't collide with the top nav links;
    # the full project name still appears in page titles.
    "logo": {
        "text": "Learn Spark from Zero",
    },
}

# -- Options for myst_nb -------------------------------------------------
# https://myst-nb.readthedocs.io/en/latest/

nb_execution_allow_errors = True
nb_execution_mode = "off"

# -- Options for copybutton -------------------------------------------------
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html

# Strip input prompts from copied code
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# By default, the copy button copies all the text in a code cell, including prompts.
# Setting this to False will make it copy only the code, without the prompts.
copybutton_only_copy_prompt_lines = False

# -- Options for sphinxcontrib-mermaid ---------------------------------------
# https://github.com/mgaitan/sphinxcontrib-mermaid

mermaid_params = ['--theme', 'forest', '--width', '600', '--backgroundColor', 'transparent']
myst_fence_as_directive = ["mermaid"]
