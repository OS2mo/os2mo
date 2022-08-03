SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <router-link :to="{ name: 'AdminPanel' }">
    <button type="button" aria-label="Administration" class="btn btn-link text-white">
      <icon name="flask" />
    </button>
  </router-link>
</template>

<script>
import "vue-awesome/icons/flask"

export default {}
</script>
