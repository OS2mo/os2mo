<template>
  <div class="card col-sm-12 col-md-12">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="folder-o"/>
        Overblik
      </h4>
      <mo-tree-view :org-uuid="orgUuid" linkable/>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import MoTreeView from '@/components/MoTreeView/MoTreeView'

  export default {
    components: {
      MoTreeView
    },
    computed: {
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })
    }
  }
</script>
