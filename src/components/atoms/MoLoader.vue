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
  export default {
    name: 'MoLoader'
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #wrapper {
    width: 48px;
    display: block;
    margin: auto;
  }
</style>