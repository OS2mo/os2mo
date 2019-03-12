import Validate from '@/api/Validate'

export default {
  validate (value, args) {
    let addressType = args

    return Validate.address(value, addressType)
  },

  getMessage (value, args, data) {
    return data
  }
}
