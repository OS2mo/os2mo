<template>
<div class="card">
  <div class="card-body">
    <h5>Worklog</h5>
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailUnit' }">
            Arbejdslog
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailLocation' }">
            Begivenheder
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailContact' }">
            Fejl
          </router-link>
        </li>
      </ul>
  </div>
</div>
</template>

<script>
    export default {
      name: 'worklog'
    }
</script>

<style scoped>
 
</style>
