#!/usr/bin/env python3

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["myst_parser", "sphinx_inline_tabs"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# General information about the project.
project = "Linux Show Player"
copyright = "Francesco Ceruti"
author = "Francesco Ceruti"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "0.6"
# The full version, including alpha/beta/rc tags.
release = "0.6.5"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for MyST -----------------------------------------------------

myst_heading_anchors = 3

myst_enable_extensions = ["attrs_inline"]

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_logo = "_static/logo.png"

html_title = project

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css",
]

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "LinuxShowPlayerdoc"

# -- Options for LaTeX output ---------------------------------------------
latex_toplevel_sectioning = "section"
latex_elements = {
    "preamble": """\
\\let\\oldsection\\section
\\renewcommand\\section{\\clearpage\\oldsection}""",
    "figure_align": "H",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "LinuxShowPlayer.tex",
        "Linux Show Player User Documentation",
        "Francesco Ceruti",
        "article",
    )
]
