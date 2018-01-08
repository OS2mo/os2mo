<template>
  <div id="login-wrapper" class="col">
    <button class="btn btn-primary btn-bg col-1" v-b-modal.login>
      <icon name="user" scale="1.8"/>
      <span class="btn-text">Medarbejder</span>
    </button>
      <br>
    <button class="btn btn-success btn-bg-2 col-1" v-b-modal.login>
      <icon name="share-alt" scale="1.8"/>
      <span class="btn-text">Organisation</span>
    </button>

    <b-modal
      id="login"
      size="md"
      hide-footer
      title="Log ind">

      <br>
      <b-form >
      <b-form-input
        class="col-8 input-center"
        name="username"
        type="text"
        placeholder="Brugernavn">
      </b-form-input>
        <br>
      <b-form-input
        class="col-8 input-center"
        name="password"
        type="password"
        placeholder="Adgangskode">
      </b-form-input>
        <br>
      <b-form-checkbox
        class="checkbox-input"
        id="checkbox1"
        value="accepted">
        Husk mig
      </b-form-checkbox>
        <br>
      <button class="btn btn-primary col-8 btn-bg" v-b-modal.login>
        Log ind
      </button>
      </b-form>
      <br>
    </b-modal>
  </div>
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

  #login-wrapper {
    text-align: center;
    margin-top: 200px;
  }

  .btn-text{
    float: right;
    margin-right: 20px;
    margin-top: 5px;
    vertical-align: middle;
    font-size: 18px;
  }

  .btn-bg{
    background-color: #4a5a79;
    cursor: pointer;
  }

  .btn-bg-2{
    cursor: pointer;
    margin-top: 10px;
    margin-right: 5px;
  }

  .btn-bg:hover{
    background-color: #002f5d;
  }

  .input-center{
    margin-left: auto;
    margin-right: auto;
  }

  .checkbox-input{
    margin-right: 215px;
    margin-bottom: 20px;
  }

</style>
