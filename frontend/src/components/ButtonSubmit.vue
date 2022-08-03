SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <button
      type="submit"
      class="btn btn-primary"
      v-if="!isLoading"
      :disabled="disabled"
    >
      <icon name="check" />
    </button>

    <mo-loader v-else />
  </div>
</template>

<script>
/**
 * A button submit component.
 */

import MoLoader from "@/components/atoms/MoLoader"
export default {
  components: {
    MoLoader,
  },

  props: {
    /**
     * This boolean property defines the loading.
     */
    isLoading: Boolean,

    disabled: Boolean,
  },
}
</script>
