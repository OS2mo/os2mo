<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="folder-o"/>
        Overblik
      </h4>
      <organisation-picker />
      <tree-view v-model="selectedOrgUnit" :orgUuid="org.uuid"/>
    </div>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import OrganisationPicker from '../components/OrganisationPicker'
  import TreeView from '../components/Treeview'
  import { EventBus } from '../EventBus'

  export default {
    components: {
      OrganisationPicker,
      TreeView
    },
    data () {
      return {
        selectedOrgUnit: {},
        org: {}
      }
    },
    watch: {
      selectedOrgUnit (newVal, oldVal) {
        this.$router.push({
          name: 'OrganisationDetail',
          params: { uuid: newVal.uuid }
        })
      }
    },
    created () {
      this.getSelectedOrganisation()
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        this.org = newOrg
      })
    },
    methods: {
      getSelectedOrganisation () {
        this.org = Organisation.getSelectedOrganisation()
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.workflow-padding {
  padding-right: 75px;
}

</style>