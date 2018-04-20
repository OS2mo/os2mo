<template>
  <div>
    <mo-navbar/>

    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>

<script>
  import MoNavbar from '@/components/MoNavbar'

  export default {
    components: {
      MoNavbar
    },
    name: 'MoBase'
  }
</script>

<style>
  .container-top-margin {
    margin-top: 4em;
  }

</style>
