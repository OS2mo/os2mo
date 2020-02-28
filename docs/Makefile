# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
PYTHON = python3
SPHINXOPTS    =
SPHINXBUILD   = ../backend/venv/bin/sphinx-build
ifeq ($(realpath $(SPHINXBUILD)),)
SPHINXBUILD   = $(PYTHON) -msphinx
endif
SPHINXPROJ    = MORa
SOURCEDIR     = .
BUILDDIR      = out

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
