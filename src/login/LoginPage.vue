<template>
  <div id="login-wrapper" class="col">
    <button class="btn btn-primary btn-bg" v-b-modal.login>
      <icon name="user" scale="1.8"/>
      <span class="btn-text">Medarbejder</span>
    </button>
      <br>
    <button class="btn btn-success btn-bg-2" v-b-modal.login>
      <icon name="share-alt" scale="1.8"/>
      <span class="btn-text">Organisation</span>
    </button>
    <login-modal/>
  </div>

</template>

<script>
  import LoginModal from './LoginModal'

  export default {
    components: {
      LoginModal
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  #login-wrapper {
    text-align: center;
    margin-top: 200px;
  }

  .btn-text {
    float: right;
    margin-left: 1em;
    margin-top: 5px;
    vertical-align: middle;
    font-size: 18px;
  }

  .btn-bg {
    background-color: #4a5a79;
    cursor: pointer;
  }

  .btn-bg-2 {
    cursor: pointer;
    margin-top: 10px;
    margin-right: 5px;
  }

  .btn-bg:hover{
    background-color: #002f5d;
  }

</style>
