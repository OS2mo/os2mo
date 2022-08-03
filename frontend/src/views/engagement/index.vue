SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="row">
    <div class="col-12 workflow-padding">
      <router-view :key="route.params.uuid" />

      <mo-log />
    </div>
  </div>
</template>

<script>
/**
 * A employee component.
 */
import { mapState } from "vuex"
import MoLog from "@/components/MoLog/MoLog"

export default {
  components: {
    MoLog,
  },
  computed: {
    ...mapState({
      route: "route",
    }),
  },
}
</script>

<style scoped>
@media (min-width: 768px) {
  .workflow-padding {
    padding-right: 75px;
  }
}

@media (max-width: 768px) {
  .workflow-padding {
    padding-top: 30px;
  }
}
</style>
