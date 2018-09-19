<template>
  <b-modal 
    id="orgUnitMove"
    ref="orgUnitMove"
    size="lg" 
    :title="$t('workflows.organisation.move_unit')"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="moveOrganisationUnit">
      <div class="form-row">
        <div class="col">
          <mo-organisation-unit-picker
            v-model="original" 
            :label="$t('input_fields.choose_unit')"
            :date="move.data.validity.from"
            required
          />
        </div>

        <div class="form-group col">
          <label>{{$t('input_fields.current_super_unit')}}</label>
          <input 
            type="text" 
            class="form-control" 
            :value="currentUnit"
            disabled
          >
        </div>
      </div>

      <mo-organisation-unit-picker
        class="parentUnit"
        v-model="move.data.parent" 
        :label="$t('input_fields.select_new_super_unit')"
        :date="move.data.validity.from"
        required
      />
      
      <div class="form-row">
        <mo-date-picker
          class="moveDate"
          :label="$t('input_fields.move_date')"
          v-model="move.data.validity.from"
          required
        />
      </div>

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div> 
    </form>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import '@/filters/GetProperty'

  export default {
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      MoOrganisationUnitPicker,
      MoDatePicker,
      ButtonSubmit
    },

    computed: {
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },

    data () {
      return {
        currentUnit: '',
        uuid: '',
        original: null,
        move: {
          type: 'org_unit',
          data: {
            validity: {}
          }
        },
        isLoading: false,
        backendValidationError: null
      }
    },

    watch: {
      original: {
        handler (newVal) {
          if (this.original) return this.getCurrentUnit(newVal.uuid)
        },
        deep: true
      }
    },

    methods: {
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      moveOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true

          OrganisationUnit.move(this.original.uuid, this.move)
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.orgUnitMove.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      },

      getCurrentUnit (unitUuid) {
        let vm = this
        if (!unitUuid) return
        OrganisationUnit.get(unitUuid)
          .then(response => {
            vm.currentUnit = response.parent ? response.parent.name : ''
          })
      }
    }
  }
</script>
