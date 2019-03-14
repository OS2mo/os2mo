import Validate from '@/api/Validate'
import i18n from '../i18n.js'

export default {
  validate (value, args) {
    let orgUnit = args[0]
    let parent = args[1]
    let validity = args[2]

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from) {
      return true
    }

    return Validate.candidateParentOrgUnit(orgUnit, parent, validity)
  },

  getMessage (field, args, key) {
    let messages = i18n.messages[i18n.locale]
    return messages.alerts.error[key]
  }
}
