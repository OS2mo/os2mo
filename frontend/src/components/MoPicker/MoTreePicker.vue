SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group">
    <label :for="nameId">{{ label }}</label>
    <input
      :name="nameId"
      :id="nameId"
      :data-vv-as="label"
      :ref="nameId"
      type="text"
      class="form-control"
      autocomplete="off"
      :placeholder="label"
      v-model="unitName"
      @click.stop="toggleTree()"
      v-validate="validations"
    />

    <div class="mo-input-group" v-show="showTree">
      <mo-tree-view
        v-model="selectedSuperUnitUuid"
        ref="moTreeView"
        :disabled-unit="disabledUnit && disabledUnit.uuid"
        :at-date="validity && validity.from"
        :get_ancestor_tree="get_ancestor_tree"
        :get_toplevel_children="get_toplevel_children"
        :get_children="get_children"
        :get_store_uuid="get_store_uuid"
      />
    </div>

    <div
      class="mo-input-group search-results"
      v-show="searchResults.length > 0 || searchResultLoading"
    >
      <mo-loader v-show="searchResultLoading" />
      <a
        href="#"
        v-show="!searchResultLoading"
        v-for="(result, index) in searchResults"
        :key="index"
        @click.prevent="selectSearchResult(result)"
      >
        <span v-for="(part, index) in result.path" :key="index">
          {{ part }}
          <span v-if="index != result.path.length - 1">&raquo;</span>
        </span>
      </a>
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A tree picker component.
 */

import MoTreeView from "@/components/MoTreeView/MoTreeView"
import MoLoader from "@/components/atoms/MoLoader"

export default {
  name: "MoTreePicker",

  components: {
    MoTreeView,
    MoLoader,
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a default label name.
     */
    label: String,

    /**
     * This boolean property disable the value.
     */
    isDisabled: Boolean,

    /**
     * This boolean property requires a valid name.
     */
    required: Boolean,

    /**
     * An object of the validities, used for validation
     */
    validity: {
      type: [Object, undefined],
      required: false,
    },

    /**
     * Unselectable unit.
     */
    disabledUnit: Object,

    /**
     * An object of additional validations to be performed
     */
    extraValidations: Object,
  },

  data() {
    return {
      /**
       * The selectedSuperUnitUuid, showTree, unitName component value.
       * Used to detect changes and restore the value.
       */
      selectedSuperUnitUuid: null,
      showTree: false,
      unitUuid: null,
      unitName: null,
      // Data for the search results
      searchResults: [],
      searchResultLoading: false, // true if results are currently loading
      searchResultSelected: false, // true if a result was just selected
    }
  },

  computed: {
    /**
     * Get name.
     */
    nameId() {
      return this.get_name_id()
    },

    /**
     * When its not disable, make it required.
     */
    isRequired() {
      if (this.isDisabled) return false
      return this.required
    },

    validations() {
      let validations = {
        required: this.required,
      }
      let subclass_validations = this.get_validations()
      if (this.extraValidations) {
        validations = {
          ...validations,
          ...subclass_validations,
          ...this.extraValidations,
        }
      }
      return validations
    },
  },

  watch: {
    /**
     * Whenever selectedSuperUnit change, update newVal.
     */
    async selectedSuperUnitUuid(newVal) {
      if (!newVal) {
        return
      }

      let unit = await this.get_entry(newVal)

      this.unitName = unit.name
      this.unitUuid = unit.uuid
      this.$refs[this.nameId].blur()
      this.showTree = false

      await this.$emit("input", unit)

      // NB: we don't perform validations until _after_ we've notified
      // the model using the event above. this avoids a race condition
      // where the extraValidations refer to our model (see #29570)
      this.$validator.validate(this.nameId)
    },

    validity: {
      deep: true,
      async handler(newVal, oldVal) {
        if (this.unitUuid) {
          let unit = await this.get_entry(this.unitUuid)

          if (!unit) {
            this.showTree = false
            this.unitName = null
            this.unitUuid = null
            this.$emit("input", null)
          }
        }

        if (newVal && (newVal.from || newVal.to)) {
          this.$refs.moTreeView.updateValidity(newVal)
        }
      },
    },
  },

  mounted() {
    /**
     * Called after the instance has been mounted.
     * Set selectedSuperUnitUuid as value.
     */
    this.selectedSuperUnitUuid = this.value
      ? this.value.uuid
      : this.selectedSuperUnitUuid
  },

  methods: {
    /**
     * Set showTree to not show.
     */
    toggleTree() {
      this.showTree = !this.showTree
    },

    /**
     * Get name.
     */
    get_name_id() {
      console.log("Not overridden: get_name_id!")
    },

    /**
     * Get extra validations.
     * @returns {Object} Object of validations to run.
     */
    get_validations() {
      return {}
    },

    /**
     * Get ancestor tree for the current entry.
     * @param {String} uuid - Uuid for the current entry
     * @param {Date} date - Date for which to lookup the tree
     * @returns {Object} Ancestor tree structure
     */
    get_ancestor_tree(uuid, date) {
      console.log("Not overridden: get_ancestor_tree!")
    },

    /**
     * Get top-level children for the top-level entry.
     * @param {String} uuid - Uuid for the top-level entry
     * @param {Date} date - Date for which to lookup the tree
     * @returns {Object} Direct children of the top-level entry
     */
    get_toplevel_children(uuid, date) {
      console.log("Not overridden: get_toplevel_children!")
    },

    /**
     * Get children for the current entry.
     * @param {String} uuid - Uuid for the current entry
     * @param {Date} date - Date for which to lookup the tree
     * @returns {Object} Direct children of the current entry
     */
    get_children(uuid, date) {
      console.log("Not overridden: get_children!")
    },

    /**
     * Get store getter for uuid.
     * @returns {String} Key to get store getter for uuid
     */
    get_store_uuid() {
      console.log("Not overridden: get_map_getters!")
    },

    /**
     * Get object for current entry.
     * @param {String} uuid - Uuid of the current entry to fetch
     * @returns {Object} Full object for the current entry
     */
    async get_entry(newVal) {
      console.log("Not overridden: get_entry!")
    },
  },
}
</script>

<style scoped>
.form-group {
  position: relative;
}
.mo-input-group {
  z-index: 999;
  background-color: #fff;
  width: 100%;
  padding: 0.375rem 0.75rem;
  position: absolute;
  border: 1px solid #ced4da;
  border-radius: 0 0 0.25rem;
  transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
}
.mo-input-group.search-results {
  max-height: 50vh;
  overflow-y: scroll;
}
.mo-input-group.search-results a {
  display: block;
}
</style>
