<template>
  <div id="wrapper">
    <icon
      class="text-primary"
      name="spinner"
      scale="3"
      spin
    />
  </div>
</template>

<script>
/**
 * A loader component.
 */
export default {
  name: 'MoLoader'
}
</script>

<style scoped>
  #wrapper {
    width: 48px;
    display: block;
    margin: auto;
  }
</style>
