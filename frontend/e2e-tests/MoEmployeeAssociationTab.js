// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import VueSelector from 'testcafe-vue-selectors'
import { Selector } from 'testcafe'
import { baseURL, setup, teardown } from './support'

let moment = require('moment')

fixture('MoEmployeeAssociationTab')
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/`)

const dialog = Selector('.modal-content')

const searchField = Selector('.navbar .v-autocomplete.search-bar')
const searchItem = searchField.find('.v-autocomplete-list-item')
const searchInput = searchField.find('input')

// Association
const parentAssociationInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const associationTypeSelect = dialog.find('.select-association select[data-vv-as="Tilknytningsrolle"]')
const associationTypeOption = associationTypeSelect.find('option')

const fromDateInput = dialog.find('.from-date .form-control')

const submitButton = dialog.find('button .btn .btn-primary')

test('Workflow: employee association tab', async t => {
  let today = moment()

  await t

    .click(searchField)
    .typeText(searchInput, 'jens')
    .expect(searchInput.value)
    .eql('jens')

    .expect(searchItem.withText(' ').visible)
    .ok('no user found - did test data change?')
    .pressKey('down enter')

    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('Tilknytninger'))

    // Create association
    .click(Selector('.btn-outline-primary').withText('Opret ny'))

    .click(parentAssociationInput)
    .click(dialog.find('.unit-association span.tree-anchor'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Projektleder'))

    .click(fromDateInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromDateInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet oprettet/
    )

    // Edit association
    .click(Selector('.edit-entry .btn-outline-primary'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Teammedarbejder'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet redigeret/
    )

    // Terminate association
    .click(Selector('.terminate-entry .btn-outline-danger'))

    .click(fromDateInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromDateInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Tilknytning med UUID [-0-9a-f]* er blevet afsluttet pr./
    )
})
