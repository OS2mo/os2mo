#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

.PHONY: all clean

PYTHON?=python3.5
NPM?=npm


all:
	$(PYTHON) -m venv venv
	./venv/bin/pip install -r requirements.txt

	$(NPM) install
	./node_modules/.bin/grunt

clean:
	$(RM) -r bower_components node_modules venv mora/__pycache__ \
  mora/static/scripts/core.js mora/static/scripts/core.js.map \
  mora/static/styles/core.css mora/static/styles/core.min.css \
  mora/static/styles/custom.css mora/static/styles/custom.min.css

