<template>
  <b-modal
    id="employeeEdit"
    size="lg"
    hide-footer 
    title="Rediger medarbejder"
    ref="employeeEdit"
  >
    <h4>Engagement</h4>
    <div>
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
              v-model="e.job_function.uuid"
              :preselected="e.job_function | getProperty('uuid')"
            />
          </td>
          <td>
            <engagement-type-picker 
              no-label
              v-model="e.engagement_type.uuid"
              :preselected="e.engagement_type | getProperty('uuid')"
            />
          </td>
          <td>
            <date-picker 
              no-label
              v-model="e.valid_from"
              :preselectedDate="new Date(e.valid_from)"
            />
          </td>
          <td>
            <date-picker
            no-label
            v-model="e.valid_to"
            :preselectedDate="new Date(e.valid_to)"
            />
          </td>
        </tr>
      </tbody>
      </table>
    </div>

      <div class="float-right">
        <button-submit @click.native="editEmployee"/>
      </div>
  </b-modal>

</template>

<script>
  import Employee from '../api/Employee'
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
    data () {
      return {
        engagements: [],
        original: []
      }
    },
    watch: {
      uuid () {
        this.getEngagements()
      }
    },
    created () {
      this.getEngagements()
    },
    methods: {
      getEngagements () {
        console.log('get engagements for edit')
        var vm = this
        Employee.getEngagementDetails(this.uuid)
        .then(response => {
          vm.engagements = response
          // make a copy that is non-reactive
          vm.original = JSON.parse(JSON.stringify(response))
        })
      },

      editEmployee () {
        let vm = this
        let edit = []
        this.engagements.forEach(function (e, index) {
          let obj = {
            type: 'engagement',
            uuid: e.uuid,
            overwrite: vm.original[index],
            data: e
          }
          edit.push(obj)
        })

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