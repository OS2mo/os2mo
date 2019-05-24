export default MODULES.map(modname => require(`./${modname}/install`).default)
