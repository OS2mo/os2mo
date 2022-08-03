SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <button
    class="btn btn-success btn-org mt-3"
    @click="$router.push({ name: 'Organisation' })"
  >
    <icon name="share-alt" scale="2" />
    <span class="btn-text">{{ $tc("shared.organisation", 1) }}</span>
  </button>
</template>
