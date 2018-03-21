<template>
  <div class="card col-sm-12 col-md-12">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="folder-o"/>
        Overblik
      </h4>
      <tree-view 
        :org="org" 
        linkable/>
    </div>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import OrganisationPicker from '../components/OrganisationPicker'
  import TreeView from '../components/Treeview'

  export default {
    components: {
      OrganisationPicker,
      TreeView
    },
    data () {
      return {
        org: {}
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        if (this.org.uuid !== newOrg.uuid) this.org = newOrg
      })
    }
  }
</script>
