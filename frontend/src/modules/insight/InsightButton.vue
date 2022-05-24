SPDX-FileCopyrightText: 2019-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
   <router-link :to="{name: 'Insight'}">
      <button type="button" :title="$t('shared.insight')" :aria-label="$t('shared.insight')" class="btn btn-primary">
        <icon name="chart-simple"/>
      </button>
  </router-link>
</template>

<script>
export default {
  
}
</script>
