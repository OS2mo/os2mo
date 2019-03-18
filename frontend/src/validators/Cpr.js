import Validate from '@/api/Validate'
import common from './common.js'

export default {
  validate (value, orgUuid) {
    return Validate.cpr(value, orgUuid)
  },

  getMessage: common.getMessage
}
