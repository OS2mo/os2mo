<template>
  <div>
    <h1>{{ msg }}</h1>
  <div class="row">
      <div class="col">
        <div class="card">
           <h1>{{ msg }}</h1>
        </div>
      </div>
      <div class="col">
        <div class="card">
           <h1>{{ msg }}</h1>
        </div>
      </div>
  </div>
  </div>
</template>

<script>
  export default {
    components: {},
    data () {
      return {
        msg: 'Her kommer tidsmaskinen'
      }
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>