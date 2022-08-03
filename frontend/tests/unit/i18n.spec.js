// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import i18n from "@/i18n.js"
import { getDatepickerLocales } from "@/i18n.js"

function symmetricDifference(setA, setB) {
  // Source:
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set#implementing_basic_set_operations
  let _difference = new Set(setA)
  for (let elem of setB) {
    if (_difference.has(elem)) {
      _difference.delete(elem)
    } else {
      _difference.add(elem)
    }
  }
  return _difference
}

function expectNoDifference(a1, a2) {
  const emptySet = new Set()
  const diff = symmetricDifference(a1, a2)
  expect(diff).toEqual(emptySet)
}

describe("i18n.js:loadLocaleMessages", () => {
  it('should detect "en" and "da" locales', async () => {
    const messages = i18n.messages
    expect(Object.keys(messages)).toEqual(expect.arrayContaining(["da", "en"]))

    const daKeys = Object.keys(messages["da"])
    const enKeys = Object.keys(messages["en"])
    expectNoDifference(daKeys, enKeys)
  })

  it("should detect the same i18n keys for all locales", async () => {
    const listAllKeys = function (obj) {
      var keys = []

      const visit = function (obj, prefix) {
        for (const [key, value] of Object.entries(obj)) {
          // If value is itself another object (e.g. a nested dictionary),
          // recurse into it.
          if (typeof value === "object") {
            visit(value, `${prefix}.${key}`)
          }
          keys.push(`${prefix}.${key}`)
        }
      }

      visit(obj, "root")
      return keys
    }

    const daKeys = listAllKeys(i18n.messages["da"])
    const enKeys = listAllKeys(i18n.messages["en"])
    expectNoDifference(daKeys, enKeys)
  })
})

describe("i18n.js:getDatepickerLocales", () => {
  it('should load "en" and "da" locales', async () => {
    const locales = getDatepickerLocales()
    expect(Object.keys(locales)).toEqual(expect.arrayContaining(["da", "en"]))

    const daKeys = Object.keys(locales["da"])
    const enKeys = Object.keys(locales["en"])
    expectNoDifference(daKeys, enKeys)
  })
})
