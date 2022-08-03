SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div id="app">
    <div class="container-top-margin">
      <router-view />
    </div>
  </div>
</template>

<script>
import { Conf } from "@/store/actions/conf"

export default {
  name: "app",

  created() {
    this.$store.dispatch(Conf.actions.SET_CONF_DB)
  },
}
</script>
