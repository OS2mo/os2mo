SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :disable-to-date="!creatingDate"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />

    <div class="form-row">
      <mo-input-text
        :label="$t('input_fields.name')"
        v-model="entry.name"
        required
      />

      <mo-input-text v-if="showUserKey"
        :label="$t('input_fields.org_unit_user_key')"
        :placeholder="$t('input_fields.org_unit_user_key_placeholder')"
        v-model="entry.user_key"
      />

      <mo-facet-picker
        facet="org_unit_type"
        v-model="entry.org_unit_type"
        required
      />

    </div>
    <div class="form-row">
      <mo-facet-picker v-if="showTimePlanning"
        facet="time_planning"
        v-model="entry.time_planning"
        required
      />

      <mo-facet-picker v-if="showOrgUnitLevel"
                       facet="org_unit_level"
                       v-model="entry.org_unit_level"
                       required
      />
    </div>

    <mo-organisation-unit-picker
      v-model="entry.parent"
      :label="$t('input_fields.select_super_unit')"
      required
      :validity="entry.validity"
    />
  </div>
</template>

<script>
/**
 * A organisation unit entry component.
 */
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import { MoInputText, MoInputDateRange } from '@/components/MoInput'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,

  name: 'MoOrganisationUnitEntry',

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
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

  computed: {
    orgUnitValidity () {
      if (this.entry.parent) {
        return this.entry.parent.validity
      }
      return this.disabledDates
    },
    showTimePlanning () {
      if (this.entry.parent) {
        return this.entry.parent.user_settings.orgunit.show_time_planning
      } else if (this.entry.user_settings) {
        return this.entry.user_settings.orgunit.show_time_planning
      }
      return false
    },
    showOrgUnitLevel () {
      if (this.entry.parent) {
        return this.entry.parent.user_settings.orgunit.show_level
      } else if (this.entry.user_settings) {
        return this.entry.user_settings.orgunit.show_level
      }
      return false
    },
    showUserKey () {
      return !this.isEdit
    }
  },

  watch: {
    /**
     * Whenever orgUnit change, update newVal.
     */
    entry: {
      handler (newVal) {
        if (newVal.user_key === undefined || newVal.user_key === ""){
          newVal.user_key = null;
        }
        this.$emit('input', newVal)
      },
      deep: true
    }
  }
}
</script>
