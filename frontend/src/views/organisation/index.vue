SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="row">
    <div class="col-sm-12 col-md-4 col-lg-4 col-xl-3">
      <div class="card">
        <div class="card-body d-flex flex-column">
          <h4 class="card-title">
            <icon name="folder-open"/>
            {{$t('common.overview')}}
          </h4>

          <div id="tree-wrapper">
            <mo-org-tree-view v-model="selected"/>
          </div>
        </div>
      </div>
    </div>

    <div class="col-sm-12 col-md-8 col-lg-8 col-xl-9 workflow-padding">
      <router-view :key="route.params.uuid"/>

    </div>

    <mo-organisation-unit-workflows/>
  </div>
</template>

<script>
/**
 * A organisation component.
 */
import MoOrganisationUnitWorkflows from '@/views/organisation/workflows'
import MoOrgTreeView from '@/components/MoTreeView/MoOrgTreeView'
import { mapState } from 'vuex'

export default {
  components: {
    MoOrganisationUnitWorkflows,
    MoOrgTreeView
  },
  computed: {
    /**
     * Get organisation uuid.
     */
    selected: {
      set (val) {
        if (val) {
          this.$router.push({ name: 'OrganisationDetail', params: { uuid: val }, hash: this.route.hash })
        } else {
          this.$router.push({ name: 'OrganisationLandingPage' })
        }
      },

      get () {
        return this.route.params.uuid
      }
    },

    ...mapState({
      route: 'route'
    })
  }
}
</script>

<style scoped>
  @media (min-width: 768px) {
   .workflow-padding {
      padding-right: 75px;
    }
  }

  @media (max-width: 768px) {
   .workflow-padding {
      padding-top: 30px;
    }
  }

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
