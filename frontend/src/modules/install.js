// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { moduleNames } from "@/moduleNames"
export default moduleNames.map((modname) => require(`./${modname}/install`).default)
