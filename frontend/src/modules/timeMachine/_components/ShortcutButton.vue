SPDX-FileCopyrightText: 2019-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <router-link :to="{ name: 'Timemachine'}">
    <button type="button" :aria-label="$tc('common.time_machine', 1)" class="btn btn-link text-white">
      <icon name="history"/>
    </button>
  </router-link>
</template>
