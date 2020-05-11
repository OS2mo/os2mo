// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from 'testcafe'
import { baseURL, setup, teardown } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoEmployeeLeave')
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste`)

const dialog = Selector('#employeeLeave')

const searchEmployeeInput = dialog.find('.v-autocomplete[data-vv-as="Medarbejder"]')
const searchEmployeeItem = searchEmployeeInput.find('.v-autocomplete-list-item')

const leaveSelect = dialog.find('select[data-vv-as="Orlovstype"]')
const leaveOption = leaveSelect.find('option')

const engagementSelect = dialog.find('select[data-vv-as="Engagementer"]')
const engagementOption = engagementSelect.find('option')

const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: leave employee', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 60 })
    .click('.btn-employee-leave')

    .expect(dialog.exists).ok('Opened dialog')

    .click(searchEmployeeInput)
    .typeText(searchEmployeeInput.find('input'), 'erik')
    .expect(searchEmployeeItem.withText(' ').visible).ok()
    .pressKey('down enter')

    .click(engagementSelect)
    .expect(engagementOption.withText('Fakultet'))
    .ok('employee lacks an engagement')
    .click(engagementOption.withText('Fakultet'))

    .click(leaveSelect)
    .click(leaveOption.withText('Barselsorlov'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* har fået tildelt orlov/
    )
})
