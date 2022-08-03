SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <button
    class="btn btn-success btn-mapper mt-3"
    @click="$router.push({ name: 'OrganisationMapper' })"
  >
    <icon name="sitemap" scale="2" />
    <span class="btn-text">{{ $t("shared.organisation_mapping") }}</span>
  </button>
</template>
