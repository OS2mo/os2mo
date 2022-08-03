SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div v-if="!removed">
    <div class="row">
      <div class="col">
        <component
          :is="entryComponent"
          v-model="entryValue"
          :hide-org-picker="hideOrgPicker"
          :hide-employee-picker="hideEmployeePicker"
          :validity-hidden="validityHidden"
        />
      </div>
      <div class="col-1 v-center">
        <button
          @click="remove()"
          type="button"
          class="btn btn-sm btn-outline-danger"
          :title="$t('common.remove')"
        >
          <icon name="minus" />
        </button>
        <button
          @click="add()"
          type="button"
          class="btn btn-sm btn-outline-success"
          :title="$t('common.create')"
        >
          <icon name="plus" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A removable component.
 */

export default {
  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * This boolean property defines the entry.
     */
    entryComponent: {
      type: Object,
      required: true,
    },

    /**
     * This boolean property defines smallButtons.
     */
    smallButtons: Boolean,

    /**
     * This boolean property hides the validity.
     */
    validityHidden: Boolean,

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
       * The entryValue, removed component value.
       * Used to detect changes and restore the value.
       */
      entryValue: {},
      removed: false,
    }
  },

  updated() {
    /**
     * Called after data change.
     * Update entryValue.
     */
    this.$emit("input", this.entryValue)
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Set entryValue to value.
     */
    this.entryValue = this.value
  },

  methods: {
    /**
     * Remove a entryValue.
     */
    remove() {
      this.entryValue = {}
      this.removed = true
    },

    add() {
      this.$emit("add")
    },
  },
}
</script>

<style scoped>
.row {
  display: flex;
}
.row .col {
  flex-grow: 9;
}
.row .v-center {
  display: flex;
  flex-grow: 3;
  flex-direction: column;
  margin-bottom: auto;
  margin-top: auto;
}
.row .v-center button {
  margin-bottom: 0.5rem;
}
</style>
