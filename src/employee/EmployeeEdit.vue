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
        <tr v-for="e in employeeEngagement" v-bind:key="e.uuid">
          <td>
            {{e.org_unit | getProperty('name')}}
          </td>
          <td> 
            <engagement-title
              v-model="engagement.selectedTitle"
              :preselected="e.job_function | getProperty('uuid')"
            />
          </td>
          <td>
            <engagement-type 
              v-model="engagement.engagement_type_uuid"
              :preselected="e.type | getProperty('uuid')"
            />
          </td>
          <td>
            <date-picker 
              :preselectedDate="new Date(e.valid_from)"
            />
          </td>
          <td>
            <date-picker
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
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'
  import EngagementTitle from '../components/EngagementTitle'
  import EngagementType from '../components/EngagementType'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      OrganisationUnitPicker,
      UnitTypeSelect,
      EngagementTitle,
      EngagementType,
      ButtonSubmit
    },
    data () {
      return {
        engagement: {
          selectedTitle: '',
          job_title_uuid: '',
          uuid: '',
          orgUnit: ''
        },
        employeeEngagement: {}
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
          vm.employeeEngagement = response
        })
      },

      editEmployee () {
        let vm = this
        let edit = [{
          type: 'engagement',
          uuid: this.employeeEngagement[0].uuid,
          overwrite: {
            valid_from: this.dateStartEnd.startDate,
            valid_to: this.dateStartEnd.endDate,
            job_function: {
              uuid: this.engagement.selectedTitle
            },
            engagement_type: {
              uuid: this.engagement.engagement_type_uuid
            },
            org_unit: {
              uuid: this.engagement.orgUnit
            }
          },
          data: {
            valid_from: this.dateStartEnd.startDate,
            valid_to: this.dateStartEnd.endDate,
            job_function: {
              uuid: this.engagement.selectedTitle
            }
          }
        }]
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