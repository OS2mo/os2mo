import Validate from '@/api/Validate'
import i18n from '../i18n.js'

export default {
  validate (value, args) {
    let addressType = args

    return Validate.address(value, addressType)
  },

  getMessage (field, args, key) {
    let messages = i18n.messages[i18n.locale]
    return messages.alerts.error[key]
  }
}
