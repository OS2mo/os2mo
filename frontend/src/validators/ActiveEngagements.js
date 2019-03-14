import Validate from '@/api/Validate'
import i18n from '../i18n.js'

export default {
  validate (value, args) {
    let validity = args[0]
    let employee = value

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from ||
      Object.keys(employee).length === 0 || !employee) {
      return true
    }

    return Validate.activeEngagements(employee, validity)
  },

  getMessage (field, args, key) {
    let messages = i18n.messages[i18n.locale]
    return messages.alerts.error[key]
  }
}
