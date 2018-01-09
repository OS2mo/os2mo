<template>
<div class="card">
  <div class="card-body">
    <h5>Worklog</h5>
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'WorkLogDetail' }">
            Arbejdslog
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'WorkLogDetailEvents' }">
            Begivenheder
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'WorkLogDetailError' }">
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
