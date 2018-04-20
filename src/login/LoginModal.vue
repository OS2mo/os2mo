<template>
  <b-modal
    id="login"
    size="md"
    hide-footer
    title="Log ind">
    <form @submit.prevent="gotoMo()">
      <div class="form-group col">
        <b-form-input
          name="username"
          type="text"
          placeholder="Brugernavn"
          v-model="user.username"/>
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

      <button type="submit" aria-label="Log ind" class="btn btn-primary col">
        Log ind
      </button>
    </form>
  </b-modal>
</template>

<script>
  import Auth from '@/api/Auth'

  export default {
    name: 'login-modal',
    props: {
      destination: {type: String, required: true}
    },
    data () {
      return {
        user: {
          username: ''
        }
      }
    },
    methods: {
      gotoMo () {
        let vm = this
        Auth.setUser(vm.user)
          .then(response => {
            vm.$router.push({name: this.destination})
          })
      }
    }
  }
</script>
