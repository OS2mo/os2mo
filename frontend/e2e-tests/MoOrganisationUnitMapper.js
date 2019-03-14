import { ClientFunction, Selector } from 'testcafe'
import { baseURL, reset } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoOrganisationUnitMapper')
  .afterEach(reset)
  .page(`${baseURL}`)

const mapperButton = Selector('button.btn-mapper')
const saveButton = Selector('button.btn-submit')

const headerText = Selector('h3').withText('Organisationssammenkobling')

const trees = VueSelector('mo-tree-view')
const leftTree = trees.filter('.origin')
const rightTree = trees.filter('.destination')

const allNodes = trees.find('.tree-node .tree-content')
const leftNodes = leftTree.find('.tree-node .tree-content')
const rightNodes = rightTree.find('.tree-node .tree-content')

const reload = ClientFunction(() => window.location.reload())
const getPagePath = ClientFunction(() => window.location.pathname);

const tabs = VueSelector('organisation-detail-tabs bTabButtonHelper')
const links = VueSelector('mo-table-detail mo-link')

const latestLog = VueSelector('MoLog').find('.alert').nth(0)

test('View no mapping', async t => {
  await t
    .click(mapperButton)
    .expect(headerText.exists).ok()

  // has the URL changed?
    .expect(getPagePath()).eql('/organisationssammenkobling')

  // we have a left tree, but no right tree
    .expect(leftTree.exists, {timout: 3000}).ok()
    .expect(rightTree.exists).notOk()

    .expect(leftNodes.withText('Hjørring Kommune').exists, {timout: 3000}).ok()

  // ...and it's just empty
    .expect(leftTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Hjørring Kommune",
      "> Lønorganisation"
    ])

    .click(leftNodes.withText('Hjørring Kommune'))

  // the right tree appears now that we selected something
    .expect(rightTree.exists, {timeout: 3000}).ok()

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> ~~~ Hjørring Kommune ~~~",
      "> Lønorganisation"
    ])

    .click(leftNodes.withText('Hjørring Kommune').find('.tree-arrow'))
    .click(leftNodes.withText('Borgmesterens Afdeling'))

  // selecting a unit doesn't reveal it in the right tree
    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Hjørring Kommune",
      "> Lønorganisation"
    ])

    .click(rightNodes.withText('Hjørring Kommune').find('.tree-arrow'))

  // but revealing it ensures that it's disabled!
    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      {
        "Hjørring Kommune": [
          "> ~~~ Borgmesterens Afdeling ~~~",
          "> Skole og Børn",
          "Social og sundhed",
          "> Teknik og Miljø"
        ]
      },
      "> Lønorganisation"
    ])

  // verify that it has no relation
    .click(rightNodes.withText('Lønorganisation').find('.tree-arrow'))

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      {
        "Hjørring Kommune": [
          "> ~~~ Borgmesterens Afdeling ~~~",
          "> Skole og Børn",
          "Social og sundhed",
          "> Teknik og Miljø"
        ]
      },
      {
        "Lønorganisation": [
          "Borgmesterens Afdeling",
          "> Skole og Børn",
          "Social og sundhed",
          "Teknik og Miljø"
        ]
      }
    ])})


test('Writing mapping', async t => {
  await t
    .click(mapperButton)
    .expect(headerText.exists).ok()

    .expect(leftTree.exists, {timout: 3000}).ok()

    .click(leftNodes.withText('Hjørring Kommune').find('.tree-arrow'))
    .click(leftNodes.withText('Borgmesterens Afdeling'))
    .expect(rightTree.exists).ok()

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Hjørring Kommune",
      "> Lønorganisation"
    ])

    .expect(saveButton.getAttribute('disabled')).ok()

    .click(rightNodes.withText('Lønorganisation').find('.tree-arrow'))
    .click(rightNodes.withText('Borgmesterens Afdeling').find('.tree-checkbox'))

  // verify that the button becomes clickable with outstanding
  // changes, and isn't when we manually revert them
    .expect(saveButton.getAttribute('disabled')).notOk()

    .click(rightNodes.withText('Borgmesterens Afdeling').find('.tree-checkbox'))

    .expect(saveButton.getAttribute('disabled')).ok()

    .click(rightNodes.withText('Borgmesterens Afdeling').find('.tree-checkbox'))

    .expect(saveButton.getAttribute('disabled')).notOk()

  // now make some more changes
  // this may break when we update the fixtures due to tree depth; I hope not

    .click(rightNodes.withText('Skole og Børn').find('.tree-arrow'))
    .click(rightNodes.withText('IT-Support').find('.tree-checkbox'))

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Hjørring Kommune",
      {
        "Lønorganisation": [
          "✓ Borgmesterens Afdeling",
          {
            "Skole og Børn": [
              "✓ IT-Support",
              "> Skoler og børnehaver",
              "Social Indsats"
            ]
          },
          "Social og sundhed",
          "Teknik og Miljø"
        ]
      }
    ])

    .click(saveButton)

  // we logged something, right?
    .expect(latestLog.innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet redigeret/
    )

  // verify that we disable the button after a save
    .expect(saveButton.getAttribute('disabled')).ok()

  // reload the page
    .expect(reload()).notOk()

  // assert that the selection has reset
    .expect(leftTree.exists).ok()
    .expect(rightTree.exists).notOk()
    .expect(leftNodes.withText('Hjørring Kommune').exists).ok()

    .expect(leftTree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Hjørring Kommune",
      "> Lønorganisation"
    ])

    .click(leftNodes.withText('Hjørring Kommune').find('.tree-arrow'))
    .click(leftNodes.withText('Borgmesterens Afdeling'))
    .expect(rightTree.exists).ok()

  // assert that the selection has reset
    .click(leftNodes.withText('Lønorganisation').find('.tree-arrow'))
    .click(leftNodes.withText('Borgmesterens Afdeling'))
    .expect(rightTree.exists).ok()

    .click(rightNodes.withText('Hjørring Kommune').find('.tree-arrow'))

  // we shouldn't have made any changes
    .expect(saveButton.getAttribute('disabled')).ok()

  // now verify that we could load the tree as expected, and expand a
  // unit afterwards
  //
  // this may break when we update the fixtures due to tree depth; I
  // hope not

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql([
      {
        "Hjørring Kommune": [
          "> ~~~ Borgmesterens Afdeling ~~~",
          "> Skole og Børn",
          "Social og sundhed",
          "> Teknik og Miljø"
        ]
      },
      {
        "Lønorganisation": [
          "✓ Borgmesterens Afdeling",
          {
            "Skole og Børn": [
              "✓ IT-Support",
              "> Skoler og børnehaver",
              "Social Indsats"
            ]
          },
          "Social og sundhed",
          "Teknik og Miljø"
        ]
      }
    ])

    // now verify that we can actually render these units
    .navigateTo('/organisation/b6c11152-0645-4712-a207-ba2c53b391ab')
    .expect(tabs.withText('Relateret').exists)
    .ok()
    .click(tabs.withText('Relateret'))

    .expect(links.exists)
    .ok()

    // this one is currently in the first colum
    .expect(links.withText('IT-Support').count)
    .eql(1)

    // two too many :(
    .expect(links.withText('Borgmesterens Afdeling').count)
    .eql(3)

  // now go to the other one

    .navigateTo('/organisation')

    .click(allNodes.withText('Lønorganisation').find('.tree-arrow'))
    .click(allNodes.withText('Skole og Børn').find('.tree-arrow'))
    .click(allNodes.withText('IT-Support'))

    .expect(tabs.withText('Relateret').exists)
    .ok()
    .click(tabs.withText('Relateret'))

    .expect(links.exists)
    .ok()

    // is there a backreference?
    .expect(links.withText('Borgmesterens Afdeling').count)
    .eql(1)

    // this is wrong  :(
    .expect(links.withText('IT-Support').exists)
    .ok('did you fix a bug?')

    // nothing else?
    .expect(links.count)
    .eql(2, 'should be 1')
})
