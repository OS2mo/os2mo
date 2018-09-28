<template>
  <div id="login-wrapper">
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <div class="col text-center">
        <h1>Velkommen til MO</h1>
        <h4>Medarbejder | Organisation</h4>
      </div>
    </nav>

    <form @submit.prevent="gotoMo()">
      <div class="form-group col">
        <b-form-input
          name="username"
          type="text"
          placeholder="Brugernavn"
          v-model="user.username"
        />
      </div>

      <div class="form-group col">
        <b-form-input
          name="password"
          type="password"
          placeholder="Adgangskode"
          v-model="user.password"
        />
      </div>

      <div class="form-group col">
        <b-form-checkbox id="checkbox1" value="accepted">
          Husk mig
        </b-form-checkbox>
      </div>

      <div class="alert alert-danger" v-if="status">
        {{$t('alerts.error.' + status)}}
      </div>

      <button type="submit" aria-label="Log ind" class="btn btn-primary col">
        Log ind
      </button>
    </form>
  </div>
</template>

<script>
  /**
   * A login page component.
   */

  import {mapGetters} from 'vuex'
  import Service from '@/api/HttpCommon'

  export default {
    name: 'login-page',

    props: {
      /**
       * Defines a required destination.
       */
      destination: {type: String, required: true}
    },

    data () {
      return {
      /**
       * The user component value.
       * Used to detect changes and restore the value.
       */
        user: {
          username: null,
          password: null
        }
      }
    },

    computed: {
      /**
       * Get status.
       */
      ...mapGetters({
        status: 'status'
      })
    },

    methods: {
      /**
       * Go to MO after post user request.
       */
      gotoMo () {
        Service.post('/user/login', this.user)
          .then(response => {
            let redirect = this.$route.query.redirect || '/'
            window.location.replace(redirect)
          })
      }
    }
  }
</script>

<style scoped>
  h1, h4 {
    color: white;
  }
</style>
