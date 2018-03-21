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
      :is-disabled="isDisabled"
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
    components: {
      OrganisationUnitPicker,
      DatePicker,
      ButtonSubmit
    },
    computed: {
      isDisabled () {
        if (this.move.data.validity.from === null || this.original === undefined || this.move.data.parent === undefined) return true
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
        }
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
