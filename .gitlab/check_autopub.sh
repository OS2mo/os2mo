#!/bin/bash
# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

AUTOPUB_CHECK=$(autopub check)

RELEASE_MD_OK=0
if [ -z "${AUTOPUB_CHECK}" ]; then
    RELEASE_MD_OK=1
fi

TRIGGER_RELEASE_FOUND=$(echo "${CI_MERGE_REQUEST_LABELS}" | grep "trigger-release")

echo "Labels: '${CI_MERGE_REQUEST_LABELS}'"
echo "Trigger label found: '${TRIGGER_RELEASE_FOUND}'"

RELEASE_MD_REQUIRED=0
if [ -z "${TRIGGER_RELEASE_FOUND}"]; then
    RELEASE_MD_REQUIRED=1
fi

echo "RELEASE.md OK: '${RELEASE_MD_OK}'"
echo "RELEASE.md required: '${RELEASE_MD_REQUIRED}'"
