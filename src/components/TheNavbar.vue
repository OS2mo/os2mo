<template>
  <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
    <img src="/src/assets/logo/os2_small.svg" width="60px">
    
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent"
      aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'employee'}">Medarbejder</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'organisation'}">Organisation</router-link>
        </li>
      </ul>

      <search-bar class="ml-auto mr-auto"/>

      <time-machine-button/>
      
      <help-button/>

      <b-dropdown id="ddown1" variant="primary">
        <template slot="button-content">
          <icon name="user"/> Admin
        </template>
        <b-dropdown-item>
          <icon name="sign-out"/> Log ud
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </nav>
</template>

<script>
  import HelpButton from '../help/TheHelpButton'
  import TimeMachineButton from '../timeMachine/TimeMachineButton'
  import SearchBar from './TheSearchBar'

  export default {
    components: {
      HelpButton,
      TimeMachineButton,
      SearchBar
    },
    data () {
      return {
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
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