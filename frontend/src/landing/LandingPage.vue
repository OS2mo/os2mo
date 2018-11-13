<template>
  <div>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <div class="col text-center">
        <h1>{{$t('common.welcome_message')}}</h1>
        <h4>{{$t('common.welcome_tagline')}}</h4>
      </div>
    </nav>

    <div id="login-wrapper">
      <div class="col">
        <button class="btn btn-primary btn-employee" @click="setDestination('Employee')">
          <icon name="user" scale="2"/>
          <span class="btn-text">{{$tc('shared.employee', 1)}}</span>
        </button>
      </div>

      <div class="col">
        <button class="btn btn-success btn-org mt-3" @click="setDestination('Organisation')">
          <icon name="share-alt" scale="2"/>
          <span class="btn-text">{{$tc('shared.organisation', 1)}}</span>
        </button>
      </div>

      <div class="col">
        <button class="btn btn-success btn-org mt-3" @click="setDestination('OrganisationMapper')">
          <icon name="share-alt" scale="2"/>
          <span class="btn-text">{{$t('shared.organisation_mapping')}}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  /**
   * A landing page component.
   */

  export default {
    methods: {
      /**
       * Push route to destination.
       */
      setDestination (val) {
        this.$router.push({
          name: val
        })
      }
    }
  }
</script>

<style scoped>
  #login-wrapper {
    text-align: center;
    margin-top: 10em;
  }

  .btn-text {
    margin-left: 1em;
    font-size: 1.2em;
  }

  .btn-employee {
    background-color: #4a5a79;
    cursor: pointer;
    max-width: 12em;
  }

  .btn-org {
    cursor: pointer;
    max-width: 12em;
  }

  .btn-employee:hover{
    background-color: #002f5d;
  }

  h1,h4 {
    color: #ffffff;
  }
</style>
