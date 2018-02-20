<template>
  <div>
    <loading v-show="isLoading"/>
    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Enhed</th>
          <th scope="col">Rolle</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr>
          <th scope="col">Fortid</th>
        </tr>
        <tr v-for="d in detailsPast" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.role_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>

        <tr>
          <th scope="col">Nutid</th>
        </tr>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.role_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
          <td>
            <!-- <mo-edit :uuid="uuid" :content="d" type="role"/> -->
          </td>
        </tr>

        <tr>
          <th scope="col">Fremtid</th>
        </tr>
        <tr v-for="d in detailsFuture" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.role_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import '../../filters/GetProperty'
  import Loading from '../../components/Loading'
  import { EventBus } from '../../EventBus'

  export default {
    components: {
      Loading
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: [],
        isLoading: false
      }
    },
    mounted () {
      EventBus.$on('employee-changed', () => {
        this.getDetails()
      })
    },
    created () {
      this.getDetails()
    },
    methods: {
      getDetails () {
        var vm = this
        vm.isLoading = true
        Employee.getRoleDetails(this.uuid)
        .then(response => {
          vm.isLoading = false
          vm.details = response
        })
        Employee.getRoleDetails(this.uuid, 'past')
        .then(response => {
          vm.detailsPast = response
        })
        Employee.getRoleDetails(this.uuid, 'future')
        .then(response => {
          vm.detailsFuture = response
        })
      }
    }
  }
</script>
<style scoped>

th{
  background-color: #ffffff;
}

</style>