<template>
  <div>
    <label>{{ item.name }}</label>
  </div>
</template>

<script>
  /**
   * A organisation unit search template component.
   */

  export default {
    props: {
      /**
       * Defines a required item.      
       */
      item: { required: true }
    }
  }
</script>
