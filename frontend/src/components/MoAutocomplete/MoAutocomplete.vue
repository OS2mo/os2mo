SPDX-FileCopyrightText: 2021 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <autocomplete
    :search="search"
    :getResultValue="getResultValue"
    :autoSelect="true"
    :debounceTime="1000"
    @submit="onSubmit"
  >
    <template
      slot="default"
      slot-scope="{
        rootProps,
        inputProps,
        inputListeners,
        resultListProps,
        resultListListeners,
        results,
        resultProps,
      }"
    >
      <div v-bind="rootProps">
        <input
          v-bind="inputProps"
          v-on="inputListeners"
          :class="[
            'form-control autocomplete-input',
            { 'autocomplete-input-no-results': noResults },
            { 'autocomplete-input-focused': focused },
          ]"
          @focus="handleFocus"
          @blur="handleBlur"
        />
        <ul
          v-if="noResults"
          class="autocomplete-result-list"
          style="position: absolute; z-index: 1; width: 100%; top: 100%"
        >
          <li class="autocomplete-result">
            {{ $t("alerts.no_search_results") }}
          </li>
        </ul>
        <ul v-bind="resultListProps" v-on="resultListListeners">
          <li
            v-for="(result, index) in results"
            :key="resultProps[index].id"
            v-bind="resultProps[index]"
          >
            <div v-if="canDisplayParentOrgUnitName(result)">
              <small>{{ getParentOrgUnitName(result) }}</small>
            </div>
            {{ result.name }}
            <div v-for="item in result.attrs" :key="item.uuid">
              <small>
                <b>{{ item.title }}</b>
                <span>{{ item.value }}</span>
              </small>
            </div>
          </li>
        </ul>
      </div>
    </template>
  </autocomplete>
</template>

<script>
import Autocomplete from "@trevoreyre/autocomplete-vue"
import "@trevoreyre/autocomplete-vue/dist/style.css"

export default {
  name: "MoAutocomplete",

  components: {
    Autocomplete,
  },

  props: {
    search: Function,
    getResultValue: Function,
    onSubmit: Function,
  },

  data() {
    return {
      focused: false,
      value: "",
      results: [],
    }
  },

  computed: {
    noResults() {
      return this.value && this.results.length === 0
    },
  },

  methods: {
    handleFocus() {
      this.focused = true
    },

    handleBlur() {
      this.focused = false
    },

    canDisplayParentOrgUnitName(result) {
      return "path" in result && result.path !== null
    },

    getParentOrgUnitName(result) {
      if (result.path !== null) {
        return result.path[result.path.length - 2]
      }
    },
  },
}
</script>
