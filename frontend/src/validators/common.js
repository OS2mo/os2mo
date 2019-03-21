import i18n from '../i18n.js'

const getMessage = (field, args, key) => {
  let messages = i18n.messages[i18n.locale]
  let error = messages.alerts.error[key]
  if (error) {
    return error
  } else {
    // Return untranslated error string if no translation was found
    console.warn(`Unable to find translation for ${key}`)
    return key
  }
}

export default {
  getMessage: getMessage
}
