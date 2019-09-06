import Validate from '@/api/Validate'
import common from './common.js'

export default {
  validate (value, args) {
    let orgUnit = args[0]

    return Validate.isMovableOrgUnit(orgUnit)
  },

  getMessage: common.getMessage
}
