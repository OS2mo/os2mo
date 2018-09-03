<template>
  <div>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <div class="col text-center">
        <h1>Velkommen til MO</h1>
        <h4>Medarbejder | Organisation</h4>
      </div>
    </nav>

    <div id="login-wrapper">
      <div class="col">
        <button class="btn btn-primary btn-employee" @click="setDestination('Employee')">
          <icon name="user" scale="2"/>
          <span class="btn-text">Medarbejder</span>
        </button>
      </div>

      <div class="col">
        <button class="btn btn-success btn-org mt-3" @click="setDestination('Organisation')">
          <icon name="share-alt" scale="2"/>
          <span class="btn-text">Organisation</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    methods: {
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
