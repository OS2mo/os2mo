<template>
  <div id="login-wrapper">
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <div class="col text-center">
        <h1>Velkommen til MO</h1>
        <h4>Medarbejder|Organisation</h4>
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
        <b-form-checkbox
          id="checkbox1"
          value="accepted"
        >
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
  import { mapGetters } from 'vuex'
  import Service from '@/api/HttpCommon'

  export default {
    name: 'login-page',
    props: {
      destination: {type: String, required: true}
    },
    data () {
      return {
        user: {
          username: null,
          password: null
        }
      }
    },
    computed: {
      ...mapGetters({
        status: 'status'
      })
    },
    methods: {
      gotoMo () {
        Service.post('/user/login', this.user)
          .then(response => {
            let redirect = this.$route.query.redirect
            console.log(redirect)
            window.location.replace(redirect)
          })
      }
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

  h1,h4 {
    color: white;
  }

</style>
