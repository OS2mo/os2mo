<template>
  <router-link :to="{ name: 'timemachine'}">
    <button type="button" class="btn btn-link">
      <icon name="history"></icon>
    </button>
  </router-link>
</template>

<script>
  export default {
    components: {},
    name: 'TimeMachineButton',
    data () {
      return {}
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .btn-link {
    color: white;
  }
</style>