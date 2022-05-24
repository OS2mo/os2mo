// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import MoNavbar from '@/api/MoNavbar.js'

const InsightButton = () => import('./InsightButton.vue')

MoNavbar.addShortcut(InsightButton, 99)
