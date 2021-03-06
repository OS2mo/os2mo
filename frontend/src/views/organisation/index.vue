SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <Split id="split-container">
      <SplitArea :size="25">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">
              <icon name="folder-open"/>
              {{$t('common.overview')}}
            </h4>
            <div id="tree-wrapper">
              <mo-org-tree-view v-model="selected"/>
            </div>
          </div>
        </div>
      </SplitArea>
      <SplitArea :size="75">
        <router-view :key="route.params.uuid"/>
      </SplitArea>
    </Split>
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
  },

  methods: {
    updateSplitHeight (e) {
      let splitContainer = document.getElementById("split-container")
      // Set height of split to window height, minus some vertical space (80px)
      // This leaves a bit of empty space at the bottom of the viewport
      splitContainer.style.height = `${window.innerHeight - 80}px`
    }
  },

  created () {
    window.addEventListener("resize", this.updateSplitHeight);
  },

  mounted () {
    this.updateSplitHeight()
  },

  destroyed () {
    window.removeEventListener("resize", this.updateSplitHeight);
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

  .card {
    width: 100%;
  }

  .card-body {
    overflow: hidden;
    padding: 1.25rem 0 2.5rem 1.25rem;
  }

  #tree-wrapper {
    height: 100%;
    overflow-y: auto;
  }

  .unit-tree {
    display: flex;
  }

  .split {
    display: flex;
    overflow: auto;
  }
  .split.split-horizontal {
    float: none;
    height: inherit;
    overflow: auto;
  }
  .split.split-horizontal:first-child {
    overflow: hidden;
  }
  .split.split-horizontal:last-child > div {
    /* Allow contents to fill container horizontally */
    flex-grow: 1;
    /* Give some whitespace for the "workflow" buttons (which otherwise cover
    some of the contents of this div) */
    padding-right: 4rem;
  }
</style>
