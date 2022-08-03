SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <button
    class="btn btn-primary btn-employee"
    @click="$router.push({ name: 'Employee' })"
  >
    <icon name="user" scale="2" />
    <span class="btn-text">{{ $tc("shared.employee", 1) }}</span>
  </button>
</template>
