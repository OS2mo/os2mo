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
        <mo-date-picker-range class="col" v-model="rename.data.validity"/>
      </div>
      <div class="form-row">
        <mo-organisation-unit-search 
          label="Enhed" 
          class="col"
          v-model="original"
          required
        />
      </div>

      <div class="form-row">
        <mo-input v-model="rename.data.name" :label="$t('input_fields.new_name')" required/>
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
  import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
  import MoInput from '@/components/atoms/MoInput'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import { mapGetters } from 'vuex'
  
  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      MoDatePickerRange,
      MoOrganisationUnitSearch,
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

          OrganisationUnit.rename(this.original.uuid, this.rename)
            .then(response => {
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
