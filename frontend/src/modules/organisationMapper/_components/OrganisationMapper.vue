<template>
  <div>
    <h1>{{$t('shared.organisation_mapping')}}</h1>

    <div class="row">
      <div class="col">
        <div class="card">
          <mo-organisation-picker v-model="org" ignore-event/>

          <mo-tree-view v-model="orgUnit" :org-uuid="org.uuid"/>

          {{orgUnit}}
        </div>

      </div>

      <div class="col-1">
        -->
      </div>

      <div class="col">
        <div class="card">
          test
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MoOrganisationPicker from '@/components/MoPicker/MoOrganisationPicker'
import MoTreeView from '@/components/MoTreeView/MoTreeView'
export default {
  name: 'OrganisationMapper',

  components: {
    MoOrganisationPicker,
    MoTreeView
  },
  data () {
    return {
      org: {},
      orgUnit: null
    }
  }
}
</script>
