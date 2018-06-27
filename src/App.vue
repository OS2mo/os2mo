<template>
  <div id="app">
    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import {AUTH_LOGOUT} from '@/vuex/actions/auth'

  export default {
    name: 'app',
    mounted () {
      var usersnapKey = process.env.USERSNAP_KEY || null

      if (usersnapKey) {
        var s = document.createElement('script')
        s.type = 'text/javascript'
        s.async = true
        s.src = `//api.usersnap.com/load/${usersnapKey}.js`
        var x = document.getElementsByTagName('script')[0]
        x.parentNode.insertBefore(s, x)
      }
    },

    created: function () {
      let vm = this
      axios.interceptors.response.use(undefined, function (err) {
        return new Promise(function (resolve, reject) {
          if (err.response.status === 401 && err.response.config && !err.response.config.__isRetryRequest) {
          // if you ever get an unauthorized, logout the user
            vm.$store.dispatch(AUTH_LOGOUT)
            .then(() => vm.$router.push({name: 'Login'}))
          }
          throw err
        })
      })
    }
  }
</script>

<style>
  #app {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .container-top-margin {
    margin-top: 4em;
  }

</style>
