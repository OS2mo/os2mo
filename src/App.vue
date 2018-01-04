<template>
  <div id="app">
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
    name: 'app'
  }
</script>

<style>
  #app {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .container-top-margin {
    margin-top: 4em;
  }

</style>
