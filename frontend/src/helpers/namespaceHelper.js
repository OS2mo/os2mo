import reduce from 'lodash.reduce'

export default function removeNamespace (namespace, types) {
  return reduce(types, (typeObj, typeValue, typeName) => {
    typeObj[typeName] = reduce(typeValue, (obj, v, k) => {
      obj[k] = v.replace(namespace, '')
      return obj
    }, {})
    return typeObj
  }, {})
}
