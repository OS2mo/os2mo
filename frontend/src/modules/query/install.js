// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import MoNavbar from "@/api/MoNavbar.js"
import "vue-awesome/icons/exchange-alt"

const ShortcutButton = () => import("./ShortcutButton.vue")

MoNavbar.addShortcut(ShortcutButton, 100)
