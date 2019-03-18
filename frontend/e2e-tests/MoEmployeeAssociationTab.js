import VueSelector from 'testcafe-vue-selectors'
import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('MoEmployeeAssociationTab')
  .page(`${baseURL}/medarbejder/542adb9a-4ec4-44b5-a0ad-3113d2987968`)

const dialog = Selector('#nameId')

const createButtonClick = VueSelector('button btn btn-outline-primary]')

// Association
const parentAssociationInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const associationTypeSelect = dialog.find('.select-association select[data-vv-as="Tilknytningsrolle"]')
const associationTypeOption = associationTypeSelect.find('option')

test('Workflow: employee association tab', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('Tilknytninger'))

    .click(Selector('.btn-outline-primary').withText('Opret ny'))

    // Create association
    .click(dialog.find('.btn-association .btn-outline-success'))

    .click(parentAssociationInput)
    .click(dialog.find('.unit-association span.tree-anchor'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Konsulent'))
})
