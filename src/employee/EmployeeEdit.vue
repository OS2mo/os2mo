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
            <engagement-title
              no-label
              v-model="e.job_function.uuid"
              :preselected="e.job_function | getProperty('uuid')"
            />
          </td>
          <td>
            <engagement-type 
              no-label
              v-model="e.type.uuid"
              :preselected="e.type | getProperty('uuid')"
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
  import EngagementTitle from '../components/EngagementTitle'
  import EngagementType from '../components/EngagementType'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      EngagementTitle,
      EngagementType,
      ButtonSubmit
    },
    data () {
      return {
        engagements: [],
        original: []

      }
    },
    created () {
      this.getEngagements()
    },
    methods: {
      getEngagements () {
        var vm = this
        Employee.getEngagementDetails(this.$route.params.uuid)
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

        console.log(edit)

        Employee.editEmployee(this.$route.params.uuid, edit)
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