<template>
  <div>
    <mo-nav-bar/>

    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>

<script>
  import MoNavBar from '@/components/MoNavBar'

  export default {
    components: {
      MoNavBar
    },
    name: 'MoBase'
  }
</script>

<style>
  .container-top-margin {
    margin-top: 4em;
  }

</style>
