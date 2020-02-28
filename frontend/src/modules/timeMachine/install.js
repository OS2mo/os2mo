// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import MoNavbar from '@/api/MoNavbar.js'
import 'vue-awesome/icons/history'

const ShortcutButton = () => import('./_components/ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 200)
