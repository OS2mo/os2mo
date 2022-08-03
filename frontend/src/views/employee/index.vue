SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="row" id="employee">
    <div class="col-12">
      <router-view :key="route.params.uuid" />
      <mo-log />
    </div>
    <mo-employee-workflows />
  </div>
</template>

<script>
/**
 * A employee component.
 */
import { mapState } from "vuex"
import MoEmployeeWorkflows from "./MoEmployeeWorkflows"
import MoLog from "@/components/MoLog/MoLog"

export default {
  components: {
    MoEmployeeWorkflows,
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
#employee {
  padding: 0 15px 0 15px;
}
</style>
