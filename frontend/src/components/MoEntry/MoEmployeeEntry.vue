SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
    />

    <div class="form-row name">
      <label>{{ $t('shared.name') }}</label>
      <mo-input-text
        :placeholder="$t('input_fields.name')"
        v-model="entry.name"
        required
      />
    </div>
    <div class="form-row nickname">
      <label>{{ $t('shared.nickname') }}</label>
      <mo-input-text
        :placeholder="$t('input_fields.givenname')"
        v-model="entry.nickname_givenname"
      />
      <mo-input-text
        :placeholder="$t('input_fields.surname')"
        v-model="entry.nickname_surname"
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

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
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

  cleanUp (entry) {
    delete entry.givenname
    delete entry.surname
    delete entry.nickname
  },
}
</script>
