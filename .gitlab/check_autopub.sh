#!/bin/bash
# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

AUTOPUB_CHECK=$(autopub check)
TRIGGER_RELEASE_FOUND=$(echo "${CI_MERGE_REQUEST_LABELS}" | grep "trigger-release")

if [ -n "${TRIGGER_RELEASE_FOUND}"]; then
    if [ -n "${AUTOPUB_CHECK}" ]; then
        echo "We need a RELEASE.md, but none was found!"
        exit 1
    fi
fi
