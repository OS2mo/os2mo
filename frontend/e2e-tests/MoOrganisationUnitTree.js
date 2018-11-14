import { Selector } from 'testcafe'
import VueSelector from 'testcafe-vue-selectors'
import { baseURL, getTreeContents } from './support'

const dialog = Selector('#orgUnitTerminate')

const parentInput = dialog.find('input[data-vv-as="Enhed"]')

const fromInput = dialog.find('.from-date input.form-control')


const trees = new Map([
  ['', "> Ballerup Kommune"],
  ['9f42976b-93be-4e0b-9a25-0dcb8af2f6b4', "> =+= Ballerup Kommune =+="],
  ['ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc', {
    "Ballerup Kommune": [
      "Ballerup Bibliotek",
      "Ballerup Familiehus",
      "=+= Ballerup Idrætspark =+="
    ]
  }],
])


let tree = Selector('.orgunit-tree')
let treeNode = tree.find('.tree-node')
let treeAnchor = treeNode.find('.tree-anchor')
let rootNode = treeNode.withAttribute('data-id', '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4')
let selected = treeNode.filter('.selected')

let currentUnitName = Selector('.orgunit .orgunit-name')

fixture('MoOrganisationUnitTree')

for (const [selection, contents] of trees.entries()) {
  test
    .page `${baseURL}/organisation/${selection}`
    (`Load of '${selection}'`, async t => {
      await t
        .expect(treeNode.exists, {timeout: 1500})
        .notOk()
        .expect(rootNode.exists)
        .eql(selection.length > 0, {timeout: 1500})
        .expect(VueSelector('mo-tree-view').exists)
        .ok()
        .expect(VueSelector('the-left-menu mo-tree-view')
                .getVue(({ computed }) => computed.contents))
        .eql(contents)
    })
}

test
  .page `${baseURL}/organisation/`
  ('Reload', async t => {
    await t
      .expect(treeNode.exists)
      .notOk()
      .expect(rootNode.exists)
      .ok()
      .expect(currentUnitName.exists)
      .notOk()
      .click(rootNode)
      .expect(currentUnitName.innerText)
      .eql('Ballerup Kommune')
      .expect(rootNode.find('.tree-children').exists)
      .notOk()
      .click(rootNode.find('.tree-arrow'))
      .expect(rootNode.find('.tree-children').exists)
      .ok()

      .click(treeAnchor.withText('Ballerup Idrætspark'))
      .expect(currentUnitName.innerText)
      .eql('Ballerup Idrætspark')

    // okay, verify that the state crosses a reload
    await t.eval(() => location.reload(true))

    await t.expect(currentUnitName.exists, {timeout: 1000})
      .notOk()
      .expect(currentUnitName.exists)
      .ok()
      .expect(currentUnitName.innerText)
      .eql('Ballerup Idrætspark')
      .expect(selected.innerText)
      .eql('Ballerup Idrætspark')
  })

