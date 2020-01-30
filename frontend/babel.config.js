// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

module.exports = {
  presets: [
    '@vue/app',
    [
      '@babel/preset-env',
      {
        useBuiltIns: 'entry'
      }
    ]
  ]
}
