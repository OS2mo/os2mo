SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
    />

    <div class="form-row">
      <mo-input-text
        :label="$t('input_fields.name')"
        v-model="entry.name"
        required
      />
      <mo-input-text
        :label="$t('input_fields.nickname')"
        v-model="entry.nickname"
      />
    </div>
  </div>
</template>

<script>
/**
 * A organisation unit entry component.
 */
import { MoInputText, MoInputDateRange } from '@/components/MoInput'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,

  name: 'MoEmployeeEntry',

  components: {
    MoInputDateRange,
    MoInputText
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * This boolean property able the date in create organisation component.
     */
    creatingDate: Boolean
  },

  created () {
    /**
     * Called synchronously after the instance is created.
     * Set entry and contactInfo to value.
     */
    this.cleanUp()
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
        this.cleanUp()
        this.$emit('input', newVal)
      },
      deep: true
    },

    /**
     * When validity change, update newVal.
     */
    validity (newVal) {
      this.entry.validity = newVal
    }
  },

  methods: {
    /**
     * Handle the entry content.
     */

    cleanUp () {
      delete this.entry.givenname
      delete this.entry.surname
      delete this.entry.nickname_givenname
      delete this.entry.nickname_surname
    }
  }
}
</script>
