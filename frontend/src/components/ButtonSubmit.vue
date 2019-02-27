<template>
  <div>
    <button
      type="submit"
      class="btn btn-primary"
      v-if="!isLoading"
      :disabled="disabled"
    >
      <icon name="check"/>
    </button>

    <mo-loader v-else/>
  </div>
</template>

<script>
/**
 * A button submit component.
 */

import MoLoader from '@/components/atoms/MoLoader'
export default {
  components: {
    MoLoader
  },

  props: {
    /**
     * This boolean property defines the loading.
     */
    isLoading: Boolean,

    disabled: Boolean
  }
}
</script>
