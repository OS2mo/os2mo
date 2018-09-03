<template>
  <div id="mo-workflow">
    <slot></slot>
  </div>
</template>

<style scoped>
  #mo-workflow {
    position: fixed;
    right: -240px;
    top: 100px;
    z-index: 1;
  }
</style>