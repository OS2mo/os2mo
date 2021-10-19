#!/bin/bash
# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

CHECK=$(autopub check)
echo "${CHECK}"

if [ -z "${CHECK}" ]; then
    autopub prepare
    autopub build
    autopub commit
    NEW_VERSION=$(python3 -c "from toml import load; print(load('pyproject.toml')['tool']['poetry']['version'])")
    git tag "${NEW_VERSION}"
    git push origin "${NEW_VERSION}"
fi
