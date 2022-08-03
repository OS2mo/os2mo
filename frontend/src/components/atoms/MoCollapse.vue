SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="wrapper">
    <div class="card" @click="open = !open">
      <div
        class="card-header"
        v-b-toggle="nameId"
        aria-expanded="true"
        :aria-controls="nameId"
      >
        <icon class="mr-1" :name="open ? 'caret-down' : 'caret-right'" />
        <strong>{{ title }}</strong>
      </div>
    </div>

    <b-collapse :id="nameId" :visible="open" @show="$emit('show')">
      <slot></slot>
    </b-collapse>
  </div>
</template>

<script>
/**
 * A collapse component.
 */

import bCollapse from "bootstrap-vue/es/components/collapse/collapse"
import bToggleDirective from "bootstrap-vue/es/directives/toggle/toggle"

export default {
  components: {
    "b-collapse": bCollapse,
  },
  directives: {
    "b-toggle": bToggleDirective,
  },
  props: {
    /**
     * Defines a title.
     */
    title: {
      type: String,
      required: true,
    },

    /**
     * This Boolean property defines the visible.
     */
    visible: Boolean,
  },

  data() {
    return {
      /**
       * The open component value.
       * Used to detect changes and restore the value.
       */
      open: false,
    }
  },

  computed: {
    /**
     * Get name `mo-collapse`.
     */
    nameId() {
      return "mo-collapse-" + this._uid
    },
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Set open to initiallyOpen.
     */
    this.open = this.visible
    if (this.visible) this.$emit("show")
  },
}
</script>

<style scoped>
.wrapper {
  margin-top: 1em;
}

.card-header {
  border-bottom: none;
  padding: 0.25rem 1.25rem;
}
</style>
