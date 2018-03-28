<template>
  <b-modal 
    id="orgUnitMove"
    ref="orgUnitMove"
    size="lg" 
    hide-footer 
    title="Flyt enhed"
    lazy
  >
    <div class="form-row">
      <date-picker 
      label="Dato for flytning"
      v-model="move.data.validity.from"
      required
      />
    </div>

    <div class="form-row">
      <div class="col">
        <organisation-unit-picker 
          v-model="original"
          label="Fremsøg enhed"
        />
      </div>

      <div class="form-group col">
        <label for="">Nuværende overenhed</label>
        <input 
          type="text" 
          class="form-control" 
          :value="currentUnit"
          disabled
        >
      </div>
    </div>

    <organisation-unit-picker 
      v-model="move.data.parent"
      label="Angiv ny overenhed"
    />

    <div class="float-right">
      <button-submit 
      :is-disabled="!formValid"
      :is-loading="isLoading"
      :on-click-action="moveOrganisationUnit"
      />
    </div> 
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  import '../filters/GetProperty'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      OrganisationUnitPicker,
      DatePicker,
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
        original: {},
        move: {
          data: {
            validity: {}
          }
        },
        isLoading: false
      }
    },
    watch: {
      original: {
        handler (newVal) {
          this.getCurrentUnit(newVal.uuid)
        },
        deep: true
      }
    },
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      moveOrganisationUnit () {
        let vm = this
        vm.isLoading = true

        OrganisationUnit.move(this.original.uuid, this.move)
          .then(response => {
            vm.$refs.orgUnitMove.hide()
          })
          .catch(err => {
            console.log(err)
            vm.isLoading = false
          })
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
