<template>
  <b-modal 
    id="orgUnitCreate" 
    size="lg" 
    hide-footer 
    title="Opret enhed"
    ref="orgUnitCreate"
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="createOrganisationUnit">
      <mo-organisation-unit-entry
        v-model="entry" 
      />

      <mo-add-many
        :entry-component="addressEntry"
        v-model="addresses"
        has-initial-entry
      />

      <div class="float-right">
        <button-submit
        :is-loading="isLoading"
        :on-click-action="createOrganisationUnit"
        />
      </div>
    </form>
  </b-modal>

</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoOrganisationUnitEntry from '@/components/MoEntry/MoOrganisationUnitEntry'
  import MoAddMany from '@/components/MoAddMany/MoAddMany'
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    name: 'OrganisationUnitCreate',
    components: {
      ButtonSubmit,
      MoOrganisationUnitEntry,
      MoAddMany
    },
    data () {
      return {
        entry: {
          validity: {}
        },
        addresses: [],
        addressEntry: MoAddressEntry,
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
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      createOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          this.isLoading = true
  
          this.entry.addresses = this.addresses
  
          OrganisationUnit.create(this.entry)
            .then(response => {
              vm.$refs.orgUnitCreate.hide()
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
