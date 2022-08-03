SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card">
    <div class="card-body d-flex flex-column">
      <div class="input-group justify-content-md-center">
        <h3>{{ $t("input_fields.search_for_name_or_cpr") }}</h3>
      </div>
      <div class="input-group input-group-lg justify-content-md-center">
        <mo-search-bar hide-date-input />
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A employee list component.
 */

import MoSearchBar from "@/components/MoSearchBar/MoSearchBar"

export default {
  components: {
    MoSearchBar,
  },
}
</script>

<style scoped>
.card-body {
  min-height: 5vh;
  max-height: 75vh;
}
.form-control-lg {
  height: auto;
}
</style>
