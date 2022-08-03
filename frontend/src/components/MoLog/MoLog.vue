SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card card-margin">
    <div class="card-body">
      <h5>{{ $t("common.work_log") }}</h5>
      <div class="wrapper">
        <div
          class="alert alert-success mt-2"
          v-for="(log, index) in reverse(worklogs)"
          :key="index"
          role="alert"
        >
          {{ toLogString(log) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A log component.
 */
import { mapGetters } from "vuex"

export default {
  name: "MoLog",

  computed: {
    /**
     * Get worklog message.
     */
    ...mapGetters({
      worklogs: "log/getWorkLog",
    }),
  },

  methods: {
    toLogString(log) {
      let arg = typeof log.value === "string" ? { uuid: log.value } : log.value

      return this.$t(`alerts.success.${log.type}`, arg)
    },

    /**
     * Reverse message.
     */
    reverse(array) {
      return array.length ? array.slice().reverse() : array
    },
  },
}
</script>

<style scoped>
.card-margin {
  margin-top: 2em;
  min-height: 150px;
}
.wrapper {
  max-height: 10rem;
  overflow-y: auto;
}
</style>
