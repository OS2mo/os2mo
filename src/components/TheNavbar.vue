<template>
  <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
    <div class="logo col-1"/>
    
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent"
      aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Employee'}">Medarbejder</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Organisation'}">Organisation</router-link>
        </li>
      </ul>

      <organisation-picker class="ml-auto mr-auto"/>

      <search-bar class="ml-auto mr-auto"/>

      <time-machine-button/>
      
      <help-button/>

      <b-dropdown id="ddown1" variant="primary">
        <template slot="button-content">
          <icon name="user"/> {{user.username}}
        </template>
        <b-dropdown-item @click="logout()">
          <icon name="sign-out"/> Log ud
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </nav>
</template>

<script>
  import Auth from '../api/Auth'
  import { EventBus } from '../EventBus'
  import HelpButton from '../help/TheHelpButton'
  import TimeMachineButton from '../timeMachine/TimeMachineButton'
  import SearchBar from './TheSearchBar'
  import OrganisationPicker from './OrganisationPicker'

  export default {
    components: {
      HelpButton,
      TimeMachineButton,
      SearchBar,
      OrganisationPicker
    },
    data () {
      return {
        user: {}
      }
    },
    created () {
      this.user = Auth.getUser()
    },
    mounted () {
      EventBus.$on('login-success', login => {
        this.user = login
      })
    },
    methods: {
      logout () {
        this.$router.push({
          name: 'login'
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .logo {
    background-image: url('../assets/logo/os2_small.svg');
    background-repeat: no-repeat; /*Prevent showing multiple background images*/
    background-position: center;
    background-color:#002f5d;
    background-size: 60px;
    width: 60px;
    height: 50px;
    margin-left: -1em;
  }
  nav {
    height: 50px;
  }
  .nav-item {
    .nav-link {
      font-family: Oswald,Arial,sans-serif !important;
      color: #e5e0de !important;
  
      &:hover {
        border-bottom: 3px solid #cda000;
      }
    }
  
    .router-link-active {
      border-bottom: 3px solid #cda000;
    }
  }
</style>