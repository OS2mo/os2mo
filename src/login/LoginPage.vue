<template>
  <div id="login-wrapper" class="col">
    <button class="btn btn-primary btn-bg" v-b-modal.login>
      <icon name="user"/>
      Medarbejder
    </button>
    <button class="btn btn-success btn-bg-2" v-b-modal.login>
      <icon name="share-alt"/>
      Organisation
    </button>

    <b-modal
      id="login"
      size="lg"
      hide-footer
      title="Log ind">

      <b-form >
      <b-form-input
        class="col-5"
        v-model="text1"
        type="text"
        placeholder="Brugernavn">
      </b-form-input>
        <br>
      <b-form-input
        class="col-5"
        v-model="text2"
        type="password"
        placeholder="Adgangskode">
      </b-form-input>
        <br>
      <b-form-checkbox
        class="col-4"
        id="checkbox1"
        value="accepted">
        Husk mig
      </b-form-checkbox>
        <br>
      <button class="btn btn-primary col-5 btn-bg" v-b-modal.login>
        Log ind
      </button>
      </b-form>
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
  }

  .btn-bg{
  background-color: #4a5a79;
    cursor: pointer;
  }

  .btn-bg-2{
    cursor: pointer;
  }

  .btn-bg:hover{
    background-color: #002f5d;
  }

  .input-center{
    vertical-align: middle;
  }


</style>
