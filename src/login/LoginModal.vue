<template>
  <b-modal
    id="login"
    size="md"
    hide-footer
    title="Log ind">

    <!-- <b-form> -->

      <div class="form-group col">
        <b-form-input
          name="username"
          type="text"
          placeholder="Brugernavn"/>
      </div>
      <div class="form-group col">
        <b-form-input
          name="password"
          type="password"
          placeholder="Adgangskode"/>
      </div>
      <div class="form-group col">
        <b-form-checkbox
          id="checkbox1"
          value="accepted">
          Husk mig
        </b-form-checkbox>
      </div>

      <button class="btn btn-primary col" @click="gotoMo">
        Log ind
      </button>
    <!-- </b-form> -->
  </b-modal>
</template>

<script>
    export default {
      name: 'login-modal',
      methods: {
        gotoMo () {
          this.$router.push({
            name: 'home',
          })
        }
      }
    }
</script>

<style scoped>

</style>
