import VueSelector from 'testcafe-vue-selectors'
import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('MoEmployeeAssociationTab')
  .page(`${baseURL}/medarbejder/554ef7cc-4a18-478f-865f-3c2f0dd20a69`)

const dialog = Selector('.modal-content')

// Association
const parentAssociationInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const associationTypeSelect = dialog.find('.select-association select[data-vv-as="Tilknytningsrolle"]')
const associationTypeOption = associationTypeSelect.find('option')

const fromDateInput = dialog.find('.from-date .form-control')

const submitButton = dialog.find('button .btn .btn-primary')

test('Workflow: employee association tab', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('Tilknytninger'))

    // Create association
    .click(Selector('.btn-outline-primary').withText('Opret ny'))

    .click(parentAssociationInput)
    .click(dialog.find('.unit-association span.tree-anchor'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Konsulent'))

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
    .click(associationTypeOption.withText('Problemknuser'))

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

