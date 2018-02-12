<template>
  <b-modal
    id="employeeEdit"
    size="lg"
    hide-footer 
    title="Rediger medarbejder"
    ref="employeeEdit"
  >
    <h4>Engagement</h4>
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">Enhed</th>
            <th scope="col">Stillingsbetegnelse</th>
            <th scope="col">Engagementstype</th>
            <th scope="col">Startdato</th>
            <th scope="col">Slutdato</th>
          </tr>
        </thead>
      
        <tbody>
          <tr v-for="e in engagements" v-bind:key="e.uuid">
            <td>
              {{e.org_unit | getProperty('name')}}
            </td>
            <td> 
              <job-function-picker
                no-label
                v-model="e.job_function"
                :preselected="e.job_function | getProperty('uuid')"
                :org="org"
              />
            </td>
            <td>
              <engagement-type-picker 
                no-label
                v-model="e.engagement_type"
                :org="org"
              />
            </td>
            <td>
              <date-picker no-label v-model="e.validity.from"/>
            </td>
            <td>
              <date-picker no-label v-model="e.validity.to"/>
            </td>
          </tr>
        </tbody>
      </table>

    <div class="float-right">
      <button-submit @click.native="editEmployee" :is-loading="isLoading"/>
    </div>
  </b-modal>

</template>

<script>
  import Employee from '../api/Employee'
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import CompareObjects from '../mixins/CompareObjects'
  import '../filters/GetProperty'
  import DatePicker from '../components/DatePicker'
  import JobFunctionPicker from '../components/JobFunctionPicker'
  import EngagementTypePicker from '../components/EngagementTypePicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      JobFunctionPicker,
      EngagementTypePicker,
      ButtonSubmit
    },
    props: {
      uuid: String
    },
    mixins: [
      CompareObjects
    ],
    data () {
      return {
        engagements: [],
        original: [],
        org: Object,
        isLoading: false
      }
    },
    watch: {
      uuid () {
        this.getEngagements()
      }
    },
    created () {
      this.getEngagements()
      this.org = Organisation.getSelectedOrganisation()
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        this.org = newOrg
      })
    },
    methods: {
      getEngagements () {
        var vm = this
        vm.isLoading = true
        Employee.getEngagementDetails(this.uuid)
        .then(response => {
          vm.engagements = response
          // make a copy that is non-reactive
          vm.original = JSON.parse(JSON.stringify(response))
          vm.isLoading = false
        })
      },

      editEmployee () {
        let vm = this
        let edit = []
        // loop through all the engagements and add them to the edit array
        this.engagements.forEach(function (e, i) {
          console.log(vm.compareObjects(e, vm.original[i]))
          if (!vm.compareObjects(e, vm.original[i])) {
            let obj = {
              type: 'engagement',
              uuid: e.uuid,
              original: vm.original[i],
              data: e
            }
            edit.push(obj)
          }
        })
        console.log(edit)

        Employee.editEmployee(this.uuid, edit)
        .then(response => {
          vm.$refs.employeeEdit.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style> 