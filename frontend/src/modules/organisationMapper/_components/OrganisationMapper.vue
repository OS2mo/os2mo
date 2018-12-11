<template>
  <div>
    <h1>{{$t('shared.organisation_mapping')}}</h1>

    <div class="row">
      <div class="col">
        <div class="card">
          <mo-tree-view v-model="origin"/>
        </div>

      </div>

      <div class="col-1">
        <button @click="$emit('mapper:submit')" class="btn btn-primary">
        <icon name="map-signs"/>
        Sammenkobl
        </button>
      </div>

      <div class="col">
        <div class="card">
          <mo-tree-view multiple v-model="destination"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MoTreeView from '@/components/MoTreeView/MoTreeView'
import 'vue-awesome/icons/map-signs'

export default {
  name: 'OrganisationMapper',

  components: {
    MoTreeView
  },
  data () {
    return {
      origin: undefined,
      destination: undefined
    }
  },
  watch: {
    origin (newVal) {
      this.$emit('mapper:origin', newVal.uuid)
    },

    destination (newVal) {
      this.$emit('mapper:destination', [newVal.uuid])
    }
  }
}
</script>
