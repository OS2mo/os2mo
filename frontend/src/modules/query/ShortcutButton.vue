SPDX-FileCopyrightText: 2019-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
   <router-link :to="{ name: 'QueryList'}">
      <button type="button" :title="$tc('shared.query',2)" :aria-label="$tc('shared.query',2)" class="btn btn-primary">
        <icon name="exchange-alt"/>
      </button>
  </router-link>
</template>

<script>
export default {

}
</script>
