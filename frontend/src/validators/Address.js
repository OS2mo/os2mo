import Validate from '@/api/Validate'
import common from './common.js'

export default {
  validate (value, args) {
    let addressType = args

    return Validate.address(value, addressType)
  },

  getMessage: common.getMessage
}
