<template>
  <b-modal 
    id="orgUnitRename"
    ref="orgUnitRename"  
    size="lg" 
    hide-footer 
    title="Omdøb enhed"
    @hidden="resetData"
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
      <div class="form-group col">
        <label for="exampleFormControlInput1">Nyt navn</label>
        <input 
          name="name"
          type="text"
          class="form-control"
          v-model="rename.data.name"
        >
      </div>
    </div>

    <div class="form-row">
      <mo-date-picker-range class="col" v-model="rename.data.validity"/>
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
  import ButtonSubmit from '@/components/ButtonSubmit'
  
  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      MoDatePickerRange,
      MoOrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        original: {},
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
