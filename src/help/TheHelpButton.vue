<template>
  <router-link :to="{ name: 'Help'}">
    <button type="button" class="btn btn-link">
      <icon name="question-circle"></icon>
    </button>
  </router-link>
</template>

<script>
  export default {
    components: {},
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