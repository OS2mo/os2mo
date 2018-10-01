<template>
  <div>
    <label>{{ item.location.name }}</label>
  </div>
</template>

<script>
  /**
   * A address search template.
   */

  export default {
    props: {
      /**
       * Defines a item location name, which is required.
       */
      item: {
        required: true
      }
    }
  }
</script>