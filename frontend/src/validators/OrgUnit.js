import Validate from '@/api/Validate'
import i18n from '../i18n.js'

export default {
  validate (value, args) {
    let validity = args[0]
    let orgUuid = args[1]

    if (!orgUuid) {
      return true
    }

    return Validate.orgUnit(orgUuid, validity)
  },

  getMessage (field, args, key) {
    let messages = i18n.messages[i18n.locale]
    return messages.alerts.error[key]
  }
}
