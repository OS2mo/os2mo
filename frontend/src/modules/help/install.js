// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import MoNavbar from '@/api/MoNavbar.js'
import 'vue-awesome/icons/question-circle'

const ShortcutButton = () => import('./ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 300)
