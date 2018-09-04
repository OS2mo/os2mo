<template>
  <div class="card">
    <div class="card-body d-flex flex-column">
      <div class="input-group justify-content-md-center">
      <h3>Søg på medarbejderens navn eller CPR-nummer</h3>
      </div>

      <div class="input-group input-group-lg justify-content-md-center">
        <mo-search-bar class="form-control-lg col-4"/>
      </div>
    </div>
  </div>
</template>

<script>
  import MoLoader from '@/components/atoms/MoLoader'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import MoSearchBar from '@/components/MoSearchBar/MoSearchBar'

  export default {
    components: {
      MoLoader,
      MoEmployeePicker,
      MoSearchBar
    }
  }
</script>

<style scoped>
  .card-body {
    min-height: 5vh;
    max-height: 75vh;
  }
</style>
