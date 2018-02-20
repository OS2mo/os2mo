<template>
  <div>
    <loading v-show="isLoading"/>

    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Enhed</th>
          <th scope="col">Stillingsbetegnelse</th>
          <th scope="col">Tilknytningstype</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <!-- <tr>
          <th scope="col">Fortid</th>
        </tr>
        <tr v-for="d in detailsPast" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.job_function | getProperty('name')}}</td>
          <td>
              {{d.association_type | getProperty('name')}}
          </td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>

        <tr>
          <th scope="col">Nutid</th>
        </tr> -->
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.job_function | getProperty('name')}}</td>
          <td>
              {{d.association_type | getProperty('name')}}
          </td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
          <td>
            <!-- <mo-edit :uuid="uuid" :content="d" type="association"/> -->
          </td>
        </tr>

        <!-- <tr>
          <th scope="col">Fremtid</th>
        </tr>
        <tr v-for="d in detailsFuture" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.job_function | getProperty('name')}}</td>
          <td>
              {{d.association_type | getProperty('name')}}
          </td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr> -->
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import '../../filters/GetProperty'
  // import MoTable from '../../components/MoTable'
  import Loading from '../../components/Loading'

  export default {
    components: {
      // MoTable,
      Loading
    },
    props: {
      value: Object,
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
    created () {
      this.getDetails()
    },
    methods: {
      getDetails () {
        var vm = this
        vm.isLoading = true
        return Employee.getAssociationDetails(this.uuid)
        .then(response => {
          vm.isLoading = false
          vm.details = response
          return response
        })
        // Employee.getAssociationDetails(this.uuid, 'past')
        // .then(response => {
        //   vm.detailsPast = response
        // })
        // Employee.getAssociationDetails(this.uuid, 'future')
        // .then(response => {
        //   vm.detailsFuture = response
        // })
      }
    }
  }
</script>

