SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-cpr-search v-model="result" required />

    <mo-cpr-result v-model="result" />
  </div>
</template>

<script>
/**
 * A cpr component.
 */

import MoCprSearch from "./MoCprSearch"
import MoCprResult from "./MoCprResult"

export default {
  name: "MoCpr",

  components: {
    MoCprSearch,
    MoCprResult,
  },

  data() {
    return {
      /**
       * The result component value.
       * Used to detect changes and restore the value.
       */
      result: {},
    }
  },

  watch: {
    /**
     * Whenever result change update val.
     */
    result(val) {
      this.$emit("input", val)
    },
  },
}
</script>
