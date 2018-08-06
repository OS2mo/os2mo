<template>
  <div class="card">
    <div class="card-body d-flex flex-column">
      <div class="input-group justify-content-md-center">
      <h3>Søg på medarbejderens navn eller CPR-nummer</h3>
      </div>
      <div class="input-group input-group-lg justify-content-md-center">
        <!-- <mo-employee-picker
          class="input-group input-group-lg col"
          aria-label="Large"
          placeholder="Søg på medarbejder eller CPR nummer"
        />
        <span class="input-group-addon">
          <icon name="search"/>
        </span> -->
        <mo-search-bar
          class="form-control-lg col-4"
        />
      </div>
      <!-- <mo-loader v-show="isLoading"/>
      <div id="employee-list-wrapper">
        <table class="table table-striped" v-show="!isLoading">
          <thead>
            <tr>
              <th scope="col">{{$t('table_headers.person')}}</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="employee in employees" :key="employee.uuid">
              <td>
                <router-link class="nav-link" :to="{ name: 'EmployeeDetail', params: {'uuid': employee.uuid} }">
                  {{employee.name}}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div> -->
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
