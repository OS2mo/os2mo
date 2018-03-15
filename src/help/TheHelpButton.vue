<template>
  <router-link :to="{ name: 'Help'}">
    <button type="button" class="btn btn-link" v-shortkey.once="['h']" @shortkey="theAction()">
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
    methods: {
      theAction () {
        this.$router.push({name: 'Help'})
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .btn-link {
      color: white;
  }
</style>