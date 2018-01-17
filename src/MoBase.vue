<template>
  <div>
    <the-navbar/>

    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>

<script>
  import TheNavbar from './components/TheNavbar'

  export default {
    components: {
      TheNavbar
    },
    name: 'MoBase'
  }
</script>

<style>
  .container-top-margin {
    margin-top: 4em;
  }

</style>
