SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title">
        <icon name="exchange-alt" />
        {{ $tc("shared.query", 2) }}
      </h4>
      <span v-for="(q, index) in queries" :key="index">
        <icon name="download" />
        <a :href="downloadLink(q)">{{ q }}</a>
      </span>
    </div>
  </div>
</template>

<script>
import store from "./_store"
import { mapGetters } from "vuex"

const STORE_KEY = "$_queryList"

export default {
  computed: {
    ...mapGetters(STORE_KEY, {
      queries: "getQueries",
    }),
  },
  created() {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
    this.$store.dispatch(`${STORE_KEY}/getQueries`)
  },
  methods: {
    downloadLink(file) {
      return "/service/exports/" + file
    },
  },
}
</script>
