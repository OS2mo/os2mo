<template>
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
</template>

<script>
    export default {
        name: 'login-modal'
    }
</script>

<style scoped>

  .input-center{
    margin-left: auto;
    margin-right: auto;
  }

  .checkbox-input{
    margin-right: 215px;
    margin-bottom: 20px;
  }

  .btn-bg{
    background-color: #4a5a79;
    cursor: pointer;
  }

  .btn-bg:hover{
    background-color: #002f5d;
  }

</style>
