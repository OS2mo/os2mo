<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="folder-o"/>
        Overblik
      </h4>
      <organisation-picker v-model="org" />

      <tree-view 
        :orgUuid="org.uuid" 
        linkable/>
    </div>
  </div>
</template>

<script>
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
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>