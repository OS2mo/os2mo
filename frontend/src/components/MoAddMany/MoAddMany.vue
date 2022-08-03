SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <h5 :class="smallButtons ? 'h5-label' : ''">
      <button
        @click="add()"
        type="button"
        class="btn btn-outline-success"
        :class="smallButtons ? 'btn-sm' : ''"
        style="border: none !important"
      >
        <icon name="plus" />
      </button>
      {{ label }}
    </h5>
    <div v-for="(v, index) in values" :key="index">
      <mo-removable-component
        @add="add"
        :entry-component="entryComponent"
        :small-buttons="smallButtons"
        :validity-hidden="validityHidden"
        :hide-org-picker="hideOrgPicker"
        :hide-employee-picker="hideEmployeePicker"
        v-model="values[index]"
      />
    </div>
  </div>
</template>

<script>
/**
 * A add many component.
 */

import MoRemovableComponent from "./MoRemovableComponent"

export default {
  components: {
    MoRemovableComponent,
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Array,
    entryComponent: {
      type: Object,
      required: true,
    },

    /**
     * This boolean property defines the entry.
     */
    hasInitialEntry: Boolean,

    /**
     * This boolean property defines smallButtons.
     */
    smallButtons: Boolean,

    /**
     * This boolean property hides the validity.
     */
    validityHidden: Boolean,

    /**
     * Defines the label.
     */
    label: String,

    /**
     * This boolean property hide the org picker.
     */
    hideOrgPicker: Boolean,

    /**
     * This boolean property hide the employee picker.
     */
    hideEmployeePicker: Boolean,
  },

  data() {
    return {
      /**
       * The values component value.
       * Used to detect changes and restore the value.
       */
      values: [],
    }
  },

  updated() {
    /**
     * Called after data change.
     * Update value if value lenght is not 0.
     */
    let data = this.values.filter((value) => Object.keys(value).length !== 0)
    this.$emit("input", data)
  },

  mounted() {
    /**
     * Show values else add new values.
     */
    if (this.value) {
      this.values = this.value
    } else {
      if (this.hasInitialEntry) {
        this.add()
      }
    }
  },

  methods: {
    /**
     * Push new values.
     */
    add() {
      this.values.push({})
    },
  },
}
</script>

<style scoped>
.h5-label {
  font-size: 1rem;
  font-weight: 400;
}
</style>
