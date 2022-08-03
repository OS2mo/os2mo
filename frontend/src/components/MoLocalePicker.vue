SPDX-FileCopyrightText: 2021 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <b-form-radio-group
    id="locale-picker"
    v-model="currentLocale"
    buttons
    button-variant="primary"
  >
    <b-form-radio
      v-for="locale in availableLocales"
      :value="locale.code"
      :key="locale.code"
    >
      <flag :iso="locale.flag" :title="locale.name" v-bind:squared="false" />
    </b-form-radio>
  </b-form-radio-group>
</template>

<script>
import { Validator } from "vee-validate"
import bFormRadioGroup from "bootstrap-vue/es/components/form-radio/form-radio-group"
import bFormRadio from "bootstrap-vue/es/components/form-radio/form-radio"

export default {
  components: {
    "b-form-radio-group": bFormRadioGroup,
    "b-form-radio": bFormRadio,
  },

  data() {
    return {
      currentLocale: null,
      availableLocales: [
        { code: "da", flag: "dk", name: "Dansk" },
        { code: "en", flag: "gb", name: "English" },
      ],
    }
  },

  created() {
    this.currentLocale = this.$i18n.locale
    this.setLocale(this.currentLocale)
  },

  watch: {
    currentLocale: function (newVal) {
      this.setLocale(newVal)
    },
  },

  methods: {
    setLocale(locale) {
      // Set locale used by `vue-i18n`
      this.$i18n.locale = locale
      // Set locale used by `vee-validate`
      Validator.localize(locale)
      // Save locale choice to localStorage
      localStorage.moLocale = locale
    },
  },
}
</script>
