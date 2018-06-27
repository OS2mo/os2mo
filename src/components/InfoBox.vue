<template>
  <div class="col-sm-3 box text-white ml-3">
    <icon class="icon-box" :name="icon" scale="3"/>
    <p>{{label}}</p>
    <span class="text-size">{{info}}</span>
  </div>
</template>

<script>
  export default {
    props: {
      icon: {
        type: String,
        required: true
      },
      label: {
        type: String,
        required: true
      },
      info: Number
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .icon-box {
    width: 5.5vh;
    height: 5.5vh;
  }

  .box {
    margin: 0.5rem;
    background-color: #007bff;
    min-height: 10vh;
    display: block;
    text-align: center;
    padding-top: 1vh;
  }

  .text-size {
    line-height: 0vh;
    font-size: 2vh;
  }

</style>
