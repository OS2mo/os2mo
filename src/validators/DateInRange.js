const moment = require('moment')

export default {
  getMessage (field, [range]) {
    if (range.from && !range.to) {
      return `${field} skal være over ${moment(range.from).format('DD-MM-YYYY')}`
    }

    if (range.to && !range.from) {
      return `${field} skal være under ${moment(range.to).format('DD-MM-YYYY')}`
    }

    return `${field} skal være mellem ${moment(range.from).format('DD-MM-YYYY')} og ${moment(range.to).format('DD-MM-YYYY')}`
  },
  validate (value, [range]) {
    value = new Date(value)

    let aboveMin = range.from ? value > range.from : true
    let belowMax = range.to ? value < range.to : true

    return aboveMin && belowMax
  }
}
