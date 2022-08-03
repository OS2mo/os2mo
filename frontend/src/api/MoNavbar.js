// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import sortBy from "lodash.sortby"

let shortcuts = []

export default {
  /**
   * Add a shortcut
   * @param {*} template - a template view
   * @param {*} position - optional position. Lower number is to the left
   */
  addShortcut(template, position = 0) {
    shortcuts.push({
      template: template,
      position: position,
    })
  },

  /**
   * returns list of shortcuts
   * @returns {Array}
   */
  getShortcuts() {
    return sortBy(shortcuts, "position")
  },
}
