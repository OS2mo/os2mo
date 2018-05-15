<template>
  <b-modal 
    id="employeeMove" 
    size="lg" 
    :title="$t('workflows.employee.move_engagement')"
    ref="employeeMove"
    hide-footer 
    lazy
    no-close-on-backdrop
    @hidden="resetData"
  >
  <form @submit.stop.prevent="moveEmployee">
    <mo-employee-picker v-model="employee" required/>

    <div class="form-row">
      <mo-date-picker :label="$t('input_fields.move_date')" class="col" v-model="move.data.validity.from" required/>
    </div>
    
    <div class="form-row">
      <mo-engagement-picker v-model="original" :employee="employee" required/>
    </div>

    <div class="form-row">
      <mo-organisation-unit-search
        :label="$t('input_fields.move_to')" 
        class="col" 
        v-model="move.data.org_unit"
        required
      />       
    </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading"/>
    </div>

    <mo-confirm-checkbox
      :entry-date="move.data.validity.from"
      :entry-name="original.engagement_type.name"
      :entry-org-name="original.org_unit.name"
      v-if="this.dateConflict" 
      required
    />
  </form>
</b-modal>
</template>

<script>
  import Employee from '@/api/Employee'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
  import MoEngagementPicker from '@/components/MoPicker/MoEngagementPicker'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoConfirmCheckbox from '@/components/MoConfirmCheckbox'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      MoDatePicker,
      MoOrganisationUnitSearch,
      MoEngagementPicker,
      MoEmployeePicker,
      ButtonSubmit,
      MoConfirmCheckbox
    },
    props: {
      entryName: String,
      entryDate: Date,
      entryOrgName: String
    },
    data () {
      return {
        employee: {},
        isLoading: false,
        original: null,
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
      },

      dateConflict () {
        if (this.move.data.validity.from && this.original) {
          if (this.original.validity.to == null) return true
          this.move.data.validity.from = new Date(this.move.data.validity.from)
          this.original.validity.to = new Date(this.original.validity.to)
          if (this.move.data.validity.from <= this.original.validity.to) return true
        }
        return false
      }
    },
    methods: {
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      moveEmployee (evt) {
        evt.preventDefault()
        if (this.formValid) {
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
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
