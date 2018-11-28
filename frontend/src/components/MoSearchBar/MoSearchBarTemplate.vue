<template>
  <div>
    <span>{{ item.name }}</span>
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
    item: { required: true }
  }
}
</script>
