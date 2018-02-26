<template>
  <div>
    <loading v-show="isLoading"/>
    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Orlovstype</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>

      <tbody>
        <tr>
          <th scope="col">Fortid</th>
        </tr>
        <tr v-for="d in detailsPast" v-bind:key="d.uuid">
          <td>{{d.leave_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>

        <tr>
          <th scope="col">Nutid</th>
        </tr>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td>{{d.leave_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>

        <tr>
          <th scope="col">Fremtid</th>
        </tr>
        <tr v-for="d in detailsFuture" v-bind:key="d.uuid">
          <td>{{d.leave_type | getProperty('name')}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      content-type="leave"
      :loading="loading"
      :uuid="uuid"
      :edit-component="entryComponent"
    />

    <mo-entry-modal-base 
      type="CREATE" 
      :uuid="uuid" 
      label="Ny orlov" 
      :entry-component="entryComponent"
      content-type="leave"
    />
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import { EventBus } from '../../EventBus'
  import MoTableCollapsibleTense from '../../components/MoTableCollapsibleTense'
  import MoEntryModalBase from '../../components/MoEntryModalBase'
  import MoLeaveEntry from './MoLeaveEntry'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryModalBase
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: {
          present: [],
          past: [],
          future: []
        },
        loading: {
          present: false,
          past: false,
          future: false
        },
        columns: ['leave_type'],
        entryComponent: MoLeaveEntry
      }
    },
    mounted () {
      EventBus.$on('employee-changed', () => {
        this.getAllDetails()
      })
    },
    created () {
      this.getAllDetails()
    },
    methods: {
      getAllDetails () {
        let tense = ['past', 'present', 'future']

        tense.forEach(t => {
          this.getDetails(t)
        })
      },

      getDetails (tense) {
        let vm = this
        vm.loading.present = true
        Employee.getLeaveDetails(this.uuid, tense)
        .then(response => {
          vm.loading[tense] = false
          vm.details[tense] = response
        })
      }
    }
  }
</script>
