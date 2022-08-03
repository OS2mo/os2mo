// SPDX-FileCopyrightText: 2021- Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import i18n from "../i18n.js"

export let display_map = new Map()
  .set("", undefined)
  .set("engagement_priority", i18n.tc("shared.engagement", 0))
  .set("association_priority", i18n.tc("shared.association", 0))

export let inference_priority_values = [...display_map.keys()]

export function display_method(value) {
  return display_map.get(value)
}
