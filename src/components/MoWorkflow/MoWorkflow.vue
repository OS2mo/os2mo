<template>
  <div id="mo-workflow">
    <slot></slot>
  </div>
</template>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #mo-workflow {
    position: fixed;
    right: -240px;
    top: 100px;
    z-index: 1;
  }
</style>