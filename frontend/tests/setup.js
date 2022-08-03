// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import "babel-polyfill"
import Vue from "vue"

// Set up vue-awesome icons used in tests
import Icon from "vue-awesome/components/Icon"
import "vue-awesome/icons/ban"
import "vue-awesome/icons/caret-down"
import "vue-awesome/icons/caret-right"
import "vue-awesome/icons/check"
import "vue-awesome/icons/edit"
import "vue-awesome/icons/folder-open"
import "vue-awesome/icons/plus-circle"
import "vue-awesome/icons/plus"
import "vue-awesome/icons/search"
import "vue-awesome/icons/share-square"
import "vue-awesome/icons/sign-out-alt"
import "vue-awesome/icons/spinner"
import "vue-awesome/icons/user-alt"
import "vue-awesome/icons/user"
import "vue-awesome/icons/users"
import "vue-awesome/icons/exchange-alt"
Vue.component("icon", Icon)
