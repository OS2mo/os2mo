import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

const dialog = Selector('#employeeCreate')

// CPR Number
const checkbox = Selector('input[data-vv-as="checkbox"]')

// Engagement
const parentEngagementInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const parentEngagementItem = parentEngagementInput.find('.v-autocomplete-list-item label')

const jobFunctionEngagementSelect = dialog.find('select[data-vv-as="Stillingsbetegnelse"]')
const jobFunctionEngagementOption = jobFunctionEngagementSelect.find('option')

const engagementTypeSelect = dialog.find('select[data-vv-as="Engagementstype"]')
const engagementTypeOption = engagementTypeSelect.find('option')

const fromInput = dialog.find('.from-date input.form-control')

// Address
const addressTypeSelect = dialog.find('select[data-vv-as="Adressetype"]')
const addressTypeOption = addressTypeSelect.find('option')

const addressInput = dialog.find('.v-autocomplete[data-vv-as="Lokation"]')
const addressItem = addressInput.find('.v-autocomplete-list-item label')

// Association
const parentAssociationInput = dialog.find('.unit-association .v-autocomplete[data-vv-as="Enhed"]')
const parentAssociationItem = parentAssociationInput.find('.unit-association .v-autocomplete-list-item label')

const addressAssociationSelect = dialog.find('.address-association select[data-vv-as="Adresser"]')
const addressAssociationOption = addressAssociationSelect.find('option')

const jobFunctionAssociationSelect = dialog.find('.select-association select[data-vv-as="Stillingsbetegnelse"]')
const jobFunctionAssociationOption = jobFunctionAssociationSelect.find('option')

const associationTypeSelect = dialog.find('.select-association select[data-vv-as="Tilknytningstype"]')
const associationTypeOption = associationTypeSelect.find('option')

// Role
const parentRoleInput = dialog.find('.unit-role .v-autocomplete[data-vv-as="Enhed"]')
const parentRoleItem = parentRoleInput.find('.unit-role .v-autocomplete-list-item label')

const roleTypeSelect = dialog.find('.select-role select[data-vv-as="Rolletype"]')
const roleTypeOption = roleTypeSelect.find('option')

// IT System
const itSystemSelect = dialog.find('.select-itSystem select[data-vv-as="IT systemer"]')
const itSystemOption = itSystemSelect.find('option')

// Manager
const parentManagerInput = dialog.find('.unit-manager .v-autocomplete[data-vv-as="Enhed"]')
const parentManagerItem = parentManagerInput.find('.unit-manager .v-autocomplete-list-item label')

const addressManagerSelect = dialog.find('.address-manager select[data-vv-as="Adresser"]')
const addressManagerOption = addressManagerSelect.find('option')

const managerTypeSelect = dialog.find('.select-manager select[data-vv-as="Ledertyper"]')
const managerTypeOption = managerTypeSelect.find('option')

const levelManagerSelect = dialog.find('.select-manager select[data-vv-as="Lederniveau"]')
const levelManagerOption = levelManagerSelect.find('option')

const responsibilityManagerSelect = dialog.find('.responsibility-manager select[data-vv-as="Lederansvar"]')
const responsibilityManagerOption = responsibilityManagerSelect.find('option')

fixture('Employee test')
  .page(`${baseURL}/medarbejder/liste`)

test('Workflow: create employee', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .hover('#mo-workflow', {offsetX: 10, offsetY: 10})
    .click('.btn-employee-create')

    .expect(dialog.exists).ok('Opened dialog')

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), '2003920001')
    .click(dialog.find('.btn-outline-primary'))
    .click(checkbox)
    .expect(checkbox.checked).ok()

    // Engagement
    .click(parentEngagementInput)
    .typeText(parentEngagementInput.find('input'), 'fam')
    .expect(parentEngagementItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentEngagementInput.find('input').value).eql('Ballerup Familiehus')

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText('Afdelingssygeplejerske'))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText('Frivillig'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    // Address
    .click(dialog.find('.btn-address .btn-outline-success'))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText('Lokation'))

    .click(addressInput)
    .typeText(addressInput.find('input'), 'baa')
    .expect(addressItem.withText('Ved Bålpladsen 1').visible).ok()
    .pressKey('down enter')
    .expect(addressInput.find('input').value).contains('Ved Bålpladsen 1')

    // Association
    .click(dialog.find('.btn-association .btn-outline-success'))

    .click(parentAssociationInput)
    .typeText(parentAssociationInput.find('input'), 'fam')
    .expect(parentAssociationItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentAssociationInput.find('input').value).eql('Ballerup Familiehus')

    .click(addressAssociationSelect)
    .click(addressAssociationOption.withText('(Henvendelsessted) Torvevej 21, 2740 Skovlunde'))

    .click(jobFunctionAssociationSelect)
    .click(jobFunctionAssociationOption.withText('Afdelingschef'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Ansat'))

    // Role
    .click(dialog.find('.btn-role .btn-outline-success'))

    .click(parentRoleInput)
    .typeText(parentRoleInput.find('input'), 'fam')
    .expect(parentRoleItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentRoleInput.find('input').value).eql('Ballerup Familiehus')

    .click(roleTypeSelect)
    .click(roleTypeOption.withText('Tillidsmand'))

    // IT System
    .click(dialog.find('.btn-itSystem .btn-outline-success'))

    .click(itSystemSelect)
    .click(itSystemOption.withText('Active Directory'))

    // Manager
    .click(dialog.find('.btn-manager .btn-outline-success'))

    .click(parentManagerInput)
    .typeText(parentManagerInput.find('input'), 'fam')
    .expect(parentManagerItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentManagerInput.find('input').value).eql('Ballerup Familiehus')

    .click(addressManagerSelect)
    .click(addressManagerOption.withText('(Henvendelsessted) Torvevej 21, 2740 Skovlunde'))

    .click(managerTypeSelect)
    .click(managerTypeOption.withText('Direktør'))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText('Niveau 90'))

    .click(responsibilityManagerSelect)
    .click(responsibilityManagerOption.withText('IT ledelse'))

    // Submit button
    .click(dialog.find('.btn-primary'))

    .expect(Selector('#employeeCreate').exists).notOk()
})
