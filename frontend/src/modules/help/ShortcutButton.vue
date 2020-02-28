SPDX-FileCopyrightText: 2019-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <router-link :to="{ name: 'Help'}">
    <button
      type="button"
      :aria-label="$t('common.help')"
      class="btn btn-link text-white"
      v-shortkey.once="['h']"
      @shortkey="$router.push({name: 'Help'})"
    >
      <icon name="question-circle"/>
    </button>
  </router-link>
</template>
