SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <span>
    <form>
        <h6>
            <icon name="eye-slash"/>
            <label for="hide_org_unit_input">
                {{$tc('shared.hide_org_unit')}}
            </label>
            <icon id="hide_org_unit_help" name="circle-info"/>
            <b-tooltip target="hide_org_unit_help" triggers="hover">
                {{$tc('shared.hide_org_unit_help')}}
            </b-tooltip>
        </h6>
        <span id="hide_org_unit_input_wrapper" class="d-inline-block" tabindex="0">
            <input id="hide_org_unit_input" type="text" size=36 @input="update_hide_button_text" v-model="hide_uuid" pattern="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" :placeholder="uuid_placeholder" :disabled="!is_admin"/>
        </span>
        <b-tooltip target="hide_org_unit_input_wrapper" triggers="hover" :disabled="!is_admin">
            {{$tc('shared.hide_org_unit_input_help')}}
        </b-tooltip>
        <b-tooltip target="hide_org_unit_input_wrapper" triggers="hover" :disabled="is_admin">
            {{$tc('shared.field_disabled_not_admin_help')}}
        </b-tooltip>
        <span id="hide_org_unit_button_wrapper" class="d-inline-block" tabindex="0">
            <input id="hide_org_unit_button" type="button" :value="button_text" @click="hide_org_unit" :disabled="disable_button"/>
        </span>
        <b-tooltip target="hide_org_unit_button_wrapper" triggers="hover" :disabled="!disable_button">
            {{$tc('shared.hide_org_unit_button_help')}}
        </b-tooltip>
    </form>
  </span>
</template>

<script>
import 'vue-awesome/icons/eye-slash'
import bTooltip from 'bootstrap-vue/es/components/tooltip/tooltip'

import { v4 as uuidv4 } from 'uuid';
import { validate as isValidUUID } from 'uuid';

export default {
  components: {
    bTooltip,
  },
  data() {
    return {
      hide_uuid: "",
      // TODO: Use "{{$tc('shared.hide')}}" instead of Hide in value.
      button_text: "?",
      // Disable text input fields if not admin
      is_admin: true,
      // Disable button until text-field contains and UUID
      disable_button: true
    }
  },
  created () {
    this.uuid_placeholder = uuidv4()
    // TODO: Check active Keycloak token
    this.is_admin = true
  },
  methods: {
    update_hide_button_text(event) {
      // Update the hide button text and enable/disable based on the text field.
      // The button is enabled if a valid UUID has been entered.
      let hide_uuid = this.$data.hide_uuid
      if (!this.is_valid_org_unit_uuid(hide_uuid)) {
        this.$data.button_text = "?"
        this.$data.disable_button = true
        return
      }
      // TODO: Use "{{$tc('shared.hide')}}" instead of Hide in value.
      this.$data.button_text = this.is_hidden(hide_uuid) ? "Show" : "Hide"
      this.$data.disable_button = false
    },
    is_valid_org_unit_uuid(org_uuid) {
      // Check if the provided org_uuid is valid i.e. a legal and existing UUID

      // TODO: Get rid of this and get isValidUUID working
      return org_uuid.length === 36

      if (!isValidUUID(org_uuid)) {
        console.log("Not a valid UUID")
        return false
      }
      // TODO: GraphQL query to validate if the org_unit exists or not
      return true
    },
    is_hidden(org_uuid) {
      // TODO: GraphQL query to check if org_unit is hidden or not
      return true
    },
    ensure_hide_class_exists() {
      // Ensure that the 'hidden' class exists and return its uuid
      // TODO: Check if hide class exists, if not create it
      return "00000000-0000-0000-0000-000000000000"
    },
    toggle_hidden(org_uuid, hidden_class_uuid) {
      // TODO: Toggle the hidden status of the org-unit
      let is_hidden = this.is_hidden(org_uuid)
      if (is_hidden) {
        // TODO: Show
      } else {
        // TODO: Hide
      }
    },
    hide_org_unit(event) {
      let hide_uuid = this.$data.hide_uuid
      console.log(hide_uuid)

      if (!this.is_valid_org_unit_uuid(hide_uuid)) {
        // TODO: Error banner saying the UUID was not found
        return false
      }
      let hidden_class_uuid = this.ensure_hide_class_exists()
      this.toggle_hidden(hide_uuid, hidden_class_uuid)
    }
  }
}
</script>
