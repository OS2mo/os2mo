// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

export default MODULES.map(modname => require(`./${modname}/install`).default)
