<template>
  <b-modal 
    id="employeeMove" 
    size="lg" 
    title="Flyt medarbejder"
    ref="employeeMove"
    hide-footer 
    lazy
  >
    <form @submit.prevent="moveEmployee">
      <employee-picker v-model="employee" required/>

      <div class="form-row">
        <mo-date-picker label="Dato for flytning" class="col" v-model="move.data.validity.from"/>
      </div>
      
      <div class="form-row">
        <engagement-picker v-model="original" :employee="employee"/>
      </div>

      <div class="form-row">
        <organisation-unit-picker label="Angiv enhed" class="col" v-model="move.data.org_unit"/>       
      </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading" :is-disabled="!formValid"/>
    </div>
  </form>
</b-modal>
</template>

<script>
  import Employee from '@/api/Employee'
  import MoDatePicker from '@/components/MoDatePicker/MoDatePicker'
  import OrganisationUnitPicker from '@/components/OrganisationUnitPicker'
  import EngagementPicker from '@/components/EngagementPicker'
  import EmployeePicker from '@/components/EmployeePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      Employee,
      MoDatePicker,
      OrganisationUnitPicker,
      EngagementPicker,
      EmployeePicker,
      ButtonSubmit
    },
    data () {
      return {
        employee: {},
        isLoading: false,
        original: {},
        move: {
          type: 'engagement',
          data: {
            validity: {}
          }
        }
      }
    },
    computed: {
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      moveEmployee () {
        let vm = this
        vm.isLoading = true
        vm.move.uuid = this.original.uuid

        Employee.move(this.employee.uuid, [this.move])
          .then(response => {
            vm.isLoading = false
            vm.$refs.employeeMove.hide()
          })
          .catch(err => {
            console.log(err)
            vm.isLoading = false
          })
      }
    }
  }
</script>
