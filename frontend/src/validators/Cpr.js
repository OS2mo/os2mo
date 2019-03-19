import Validate from '@/api/Validate'
import common from './common.js'

export default {
  validate (value, orgUuids) {
    return Validate.cpr(value, orgUuids[0])
  },

  getMessage: common.getMessage
}
