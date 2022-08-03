SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div id="organisation">
    <Split id="split-container">
      <SplitArea :size="25">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">
              <icon name="folder-open" />
              {{ $t("common.overview") }}
            </h4>
            <div v-if="options.length > 1">
              <span>{{ $t("shared.belongs_to") }}:</span>
              <b-form-select v-model="orgUnitHierarchy" :options="options" />
            </div>
            <div id="tree-wrapper">
              <mo-org-tree-view ref="orgtree" v-model="selected" />
            </div>
          </div>
        </div>
      </SplitArea>
      <SplitArea :size="75">
        <router-view :key="route.params.uuid" />
      </SplitArea>
    </Split>
    <mo-organisation-unit-workflows />
  </div>
</template>

<script>
/**
 * A organisation component.
 */
import MoOrganisationUnitWorkflows from "@/views/organisation/workflows"
import MoOrgTreeView from "@/components/MoTreeView/MoOrgTreeView"
import { Facet } from "@/store/actions/facet"
import { Organisation } from "@/store/actions/organisation"
import { mapState } from "vuex"
import bFormSelect from "bootstrap-vue/es/components/form-select/form-select"

export default {
  components: {
    MoOrganisationUnitWorkflows,
    MoOrgTreeView,
    "b-form-select": bFormSelect,
  },

  data() {
    return {
      orgUnitHierarchy: null,
    }
  },

  computed: {
    /**
     * Get organisation uuid.
     */
    selected: {
      set(val) {
        if (val) {
          this.$router.push({
            name: "OrganisationDetail",
            params: { uuid: val },
            hash: this.route.hash,
          })
        } else {
          this.$router.push({ name: "OrganisationLandingPage" })
        }
      },
      get() {
        return this.route.params.uuid
      },
    },

    options: {
      get() {
        let facet = this.$store.getters[Facet.getters.GET_FACET]("org_unit_hierarchy")
        let result = [{ value: null, text: this.$t("shared.entire_organisation") }]
        if ("classes" in facet) {
          for (var cl of facet.classes) {
            result.push({ value: cl.uuid, text: cl.name })
          }
        }
        return result
      },
    },

    ...mapState({
      route: "route",
    }),
  },

  watch: {
    orgUnitHierarchy(newVal) {
      // Reset currently displayed org unit
      this.selected = null

      // Update org tree according to the filter value
      this.$refs.orgtree.setFilter(newVal)
    },
  },

  methods: {
    updateSplitHeight(e) {
      let splitContainer = document.getElementById("split-container")
      // Set height of split to window height, minus some vertical space (80px)
      // This leaves a bit of empty space at the bottom of the viewport
      splitContainer.style.height = `${window.innerHeight - 80}px`
    },
  },

  created() {
    window.addEventListener("resize", this.updateSplitHeight)
  },

  mounted() {
    this.updateSplitHeight()

    this.$store.dispatch(Organisation.actions.SET_ORGANISATION).then((response) => {
      this.$store.dispatch(Facet.actions.SET_FACET, { facet: "org_unit_hierarchy" })
    })
  },

  destroyed() {
    window.removeEventListener("resize", this.updateSplitHeight)
  },
}
</script>

<style scoped>
#organisation {
  padding: 0 0 0 15px;
}

.card {
  width: 100%;
}

.card-body {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  padding: 1.25rem 0 0 1.25rem;
}

select {
  display: inline-block;
  width: auto;
  margin-right: 1.25rem;
}

#tree-wrapper {
  height: 100%;
  overflow: auto;
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
