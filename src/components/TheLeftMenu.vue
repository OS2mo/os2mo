<template>
  <div class="card col-sm-12 col-md-12">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="folder-o"/>
        Overblik
      </h4>
      <tree-view 
        :org-uuid="orgUuid" 
        linkable/>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import TreeView from '../components/Treeview'

  export default {
    components: {
      TreeView
    },
    computed: {
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })
    }
  }
</script>
