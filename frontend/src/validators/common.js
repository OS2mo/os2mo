// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import i18n from "../i18n.js"

const getMessage = (field, args, error_data) => {
  let key = error_data && error_data.error_key
  let messages = i18n.messages[i18n.locale]

  let error = i18n.t(`alerts.error.${key}`, error_data)

  if (error) {
    return error
  } else {
    // Return untranslated error string if no translation was found
    console.warn(`Unable to find translation for ${key}`)
    return key
  }
}

export default {
  getMessage: getMessage,
}
