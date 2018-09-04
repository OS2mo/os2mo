<template>
  <b-modal 
    id="orgUnitRename"
    ref="orgUnitRename"  
    size="lg" 
    :title="$t('workflows.organisation.rename_unit')"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="renameOrganisationUnit">
      <div class="form-row">
        <mo-organisation-unit-picker
          label="Enhed" 
          class="col"
          v-model="original"
          required
        />
      </div>

      <div class="form-row">
        <mo-input 
          v-model="rename.data.name" 
          :label="$t('input_fields.new_name')" 
          required
        />
      </div>

      <div class="form-row">
        <mo-date-picker-range 
          class="col" 
          v-model="rename.data.validity"
        />
      </div>
      
      <div class="alert alert-danger" v-if="compareName">
        {{$t('alerts.error.COMPARE_ORG_RENAME_NAMES')}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoInput from '@/components/atoms/MoInput'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import { mapGetters } from 'vuex'
  
  export default {
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      MoDatePickerRange,
      MoOrganisationUnitPicker,
      MoInput,
      ButtonSubmit
    },

    data () {
      return {
        original: null,
        rename: {
          data: {
            name: '',
            validity: {}
          }
        },
        isLoading: false
      }
    },

    computed: {
      ...mapGetters({
        orgUnit: 'organisationUnit/getOrgUnit'
      }),

      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },

      compareName () {
        if (this.rename.data.name && this.original.name) {
          if (this.original.name == null) return true
          if (this.rename.data.name === this.original.name) return true
        }
        return false
      }
    },

    watch: {
      orgUnit: {
        handler (val) {
          this.original = val
        },
        deep: true
      }
    },

    mounted () {
      this.original = this.orgUnit
    },

    methods: {
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      renameOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true

          if (vm.compareName) {
            vm.isLoading = false
            return false
          }
          OrganisationUnit.rename(this.original.uuid, this.rename)
            .then(response => {
              vm.isLoading = false
              vm.$refs.orgUnitRename.hide()
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
