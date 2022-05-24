// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

/**
 * imports icon component and globally available icons.
 * Find more here: https://fontawesome.com/icons?d=gallery
 */
import Vue from 'vue'
import Icon from 'vue-awesome/components/Icon'

import 'vue-awesome/icons/caret-down'
import 'vue-awesome/icons/caret-right'
import 'vue-awesome/icons/spinner'
import 'vue-awesome/icons/check'
import 'vue-awesome/icons/plus'
import 'vue-awesome/icons/minus'
import 'vue-awesome/icons/edit'
import 'vue-awesome/icons/book'
import 'vue-awesome/icons/sync'
import 'vue-awesome/icons/user'
import 'vue-awesome/icons/sign-out-alt'
import 'vue-awesome/icons/search'
import 'vue-awesome/icons/sort-up'
import 'vue-awesome/icons/sort-down'
import 'vue-awesome/icons/users'
import 'vue-awesome/icons/folder-open'
import 'vue-awesome/icons/user-alt'
import 'vue-awesome/icons/share-alt'
import 'vue-awesome/icons/download'
import 'vue-awesome/icons/plus-circle'
import 'vue-awesome/icons/share-square'
import 'vue-awesome/icons/ban'
import 'vue-awesome/icons/user-plus'
import 'vue-awesome/icons/user-md'
import 'vue-awesome/icons/user-tag'
import 'vue-awesome/icons/user-times'
import 'vue-awesome/icons/user-cog'
import 'vue-awesome/icons/user-tie'
import 'vue-awesome/icons/user-lock'
import 'vue-awesome/icons/building'

Icon.register({
  'chart-simple': {
    height: 448,
    width: 512,
    d: "M160 80C160 53.49 181.5 32 208 32H240C266.5 32 288 53.49 288 80V432C288 458.5 266.5 480 240 480H208C181.5 480 160 458.5 160 432V80zM0 272C0 245.5 21.49 224 48 224H80C106.5 224 128 245.5 128 272V432C128 458.5 106.5 480 80 480H48C21.49 480 0 458.5 0 432V272zM400 96C426.5 96 448 117.5 448 144V432C448 458.5 426.5 480 400 480H368C341.5 480 320 458.5 320 432V144C320 117.5 341.5 96 368 96H400z"
  }
})

Vue.component('icon', Icon)
