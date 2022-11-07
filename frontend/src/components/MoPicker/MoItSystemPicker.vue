SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group col">
    <label :for="nameId">{{ $tc("shared.it_system", 2) }}</label>

    <select
      :name="nameId"
      :id="nameId"
      :data-vv-as="$tc('shared.it_system', 2)"
      class="form-control col"
      v-model="selected"
      @change="updateSelectedItSystem()"
      v-validate="{ required: true }"
      :disabled="disabled"
    >
      <option disabled>{{ $tc("shared.it_system", 2) }}</option>
      <option v-for="it in orderedListOptions" v-bind:key="it.uuid" :value="it.uuid">
        {{ it.name }}
      </option>
    </select>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A it system component.
 */

import sortBy from "lodash.sortby"
import Facet from "@/api/Facet"
import { EventBus, Events } from "@/EventBus"

export default {
  name: "MoItSystemPicker",

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a preselected value.
     */
    preselected: String,

    /**
     * Specifies if the picker should be enabled or not
     */
    disabled: {
      type: Boolean,
      default: false,
    },
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  data() {
    return {
      /**
       * The selected, itSystems component value.
       * Used to detect changes and restore the value.
       */
      selected: {},
      itSystems: [],
    }
  },

  computed: {
    /**
     * Get name `it-system-picker`.
     */
    nameId() {
      return "it-system-picker-" + this._uid
    },

    orderedListOptions() {
      return sortBy(this.itSystems, "name")
    },
  },

  mounted() {
    /**
     * Whenever organisation change update.
     */
    EventBus.$on(Events.ORGANISATION_CHANGED, () => {
      this.getItSystems()
    })
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Set selected to preselected.
     */
    this.selected = this.preselected
    this.getItSystems()
  },

  beforeDestroy() {
    /**
     * Stops receiving update event.
     */
    EventBus.$off([Events.ORGANISATION_CHANGED])
  },

  methods: {
    /**
     * Get it systems.
     */
    getItSystems() {
      var vm = this
      let org = this.$store.state.organisation
      if (org.uuid === undefined) return
      Facet.itSystems(org.uuid).then((response) => {
        vm.itSystems = response
      })
    },

    /**
     * Update selected it system data.
     */
    updateSelectedItSystem() {
      let data = {
        uuid: this.selected,
      }
      this.$emit("input", data)
    },
  },
}
</script>
