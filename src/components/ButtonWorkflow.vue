<template>
  <router-link :to="{ name: target}">
    <button type="button" class="btn btn-primary btn-workflow">
      <icon class="btn-icon" :name="icon"/>
      <span class="btn-label">{{label}}</span>
    </button>
  </router-link>
</template>

<script>
  export default {
    components: {},
    props: {
      label: String,
      icon: String,
      target: String
    },
    data () {
      return {}
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .btn-workflow {
    // background-color: #186847;
    // color: white;
    display: block;
    height: 38px;
    margin-bottom: 4px;
    text-align: left;
    width: 300px;
    position: relative;
    right: 0;
    transition: right .15s;
    transition-delay: .05s;
    transition-timing-function: ease-in;

    &:hover {
      right: 235px;
      transition: right .25s;
      transition-timing-function: ease-out;
    }

    .btn-label {
      padding-left: 25px;
      position: absolute;
    }

    .btn-icon {
      width: 24px;
      height: 24px;
    }
  }
</style>