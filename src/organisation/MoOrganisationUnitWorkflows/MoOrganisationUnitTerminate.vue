<template>
  <b-modal 
    id="orgUnitTerminate"
    ref="orgUnitTerminate"  
    size="lg" 
    :title="$t('workflows.organisation.terminate_unit')"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="endOrganisationUnit">
      <div class="form-row">
        <mo-organisation-unit-picker 
          :label="$tc('input_fields.unit', 1)" 
          class="col" 
          v-model="org_unit"
          required
        />
        <mo-date-picker :label="$t('input_fields.end_date')" v-model="terminate.validity.from" required/>
      </div>
      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import ButtonSubmit from '@/components/ButtonSubmit'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      MoDatePicker,
      MoOrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        org_unit: {},
        terminate: {
          validity: {}
        },
        isLoading: false
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
    methods: {
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      endOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          OrganisationUnit.terminate(this.org_unit.uuid, this.terminate)
            .then(response => {
              vm.isLoading = false
              vm.$refs.orgUnitTerminate.hide()
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
