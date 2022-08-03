// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import sortBy from "lodash.sortby"

let shortcuts = []

export default {
  /**
   * Add a menu item
   * @param {*} template - a template view
   * @param {Number} position - optional position.
   */
  addMenuItem(template, position = 0) {
    shortcuts.push({
      template: template,
      position: position * -1,
    })
  },
  /**
   * returns list of shortcuts
   * @returns {Array}
   */
  getMenu() {
    return sortBy(shortcuts, "position")
  },
}
