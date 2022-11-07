SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div :id="identifier">
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <div class="form-row">
      <mo-it-system-picker
        class="select-itSystem"
        v-model="entry.itsystem"
        :preselected="entry.itsystem && entry.itsystem.uuid"
        :disabled="disable_it_entry_edit_fields ? this.isEdit : false"
      />

      <mo-input-text
        class="input-itSystem"
        v-model="entry.user_key"
        :label="$t('input_fields.account_name')"
        required
        :disabled="disable_it_entry_edit_fields ? this.isEdit : false"
      />

      <mo-input-primary-check class="col checkbox" v-model="entry.primary" />
    </div>
  </div>
</template>

<script>
/**
 * A it system entry component.
 */
import MoItSystemPicker from "@/components/MoPicker/MoItSystemPicker"
import MoInputPrimaryCheck from "@/components/MoInput/MoInputPrimaryCheck"
import { MoInputText, MoInputDateRange } from "@/components/MoInput"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,
  name: "MoItSystemEntry",
  components: {
    MoInputText,
    MoInputDateRange,
    MoItSystemPicker,
    MoInputPrimaryCheck,
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "it"
        this.$emit("input", newVal)
      },
      deep: true,
    },
  },

  computed: {
    disable_it_entry_edit_fields() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.it_system_entry_edit_fields_disabled
    },
  },
}
</script>
