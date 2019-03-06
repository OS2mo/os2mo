import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

let moment = require('moment')

fixture('MoEmployeeAssociationTab')
  .page(`${baseURL}/medarbejder/542adb9a-4ec4-44b5-a0ad-3113d2987968`)

const dialogCreate = VueSelector('#nameId')

test('Workflow: employee association tab', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('Tilknytninger'))

    .click(dialogCreate.find('btn btn-outline-primary'))
})
