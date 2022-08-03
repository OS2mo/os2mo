SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <span
      >{{ item.name }}
      <span v-if="showUserKeyInSearch" style="color: grey">{{
        " " + item.user_key
      }}</span></span
    >
  </div>
</template>

<script>
/**
 * A searchbar template component.
 */

export default {
  props: {
    /**
     * Defines a required item name.
     */
    item: { required: true },
  },
  computed: {
    showUserKeyInSearch() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]

      return conf.show_user_key_in_search
    },
  },
}
</script>
