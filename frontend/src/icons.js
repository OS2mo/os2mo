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
    // From: https://fontawesome.com/icons/circle-info?s=solid
    "circle-info" : {
        height: 512,
        width: 512,
	    d: "M256 0C114.6 0 0 114.6 0 256s114.6 256 256 256s256-114.6 256-256S397.4 0 256 0zM256 128c17.67 0 32 14.33 32 32c0 17.67-14.33 32-32 32S224 177.7 224 160C224 142.3 238.3 128 256 128zM296 384h-80C202.8 384 192 373.3 192 360s10.75-24 24-24h16v-64H224c-13.25 0-24-10.75-24-24S210.8 224 224 224h32c13.25 0 24 10.75 24 24v88h16c13.25 0 24 10.75 24 24S309.3 384 296 384z"
    }
})

Vue.component('icon', Icon)
