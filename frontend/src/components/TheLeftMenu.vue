<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title">
        <icon name="folder-open"/>
        {{$t('common.overview')}}
      </h4>

      <div id="tree-wrapper">
        <mo-tree-view :org-uuid="orgUuid" linkable/>
      </div>
    </div>
  </div>
</template>

<script>
/**
   * A the left menu component.
   */

import { mapGetters } from 'vuex'
import MoTreeView from '@/components/MoTreeView/MoTreeView'

export default {
  components: {
    MoTreeView
  },

  computed: {
    /**
       * Get organisation uuid.
       */
    ...mapGetters({
      orgUuid: 'organisation/getUuid'
    })
  }
}
</script>

<style scoped>
.card-body {
  min-height: 5vh;
  max-height: 90vh;
  width: 100%;
}

#tree-wrapper {
  height: 100%;
  overflow-x: auto;
  overflow-y: scroll;
}
</style>
