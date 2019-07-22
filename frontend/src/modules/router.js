export default MODULES.map(modname => require(`./${modname}/router`).default)
