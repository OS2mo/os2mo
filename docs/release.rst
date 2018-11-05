Releaseprocedure
================
* Lav release branch for release iht. GitFlow, e.g. ``release/1.0.0``

* Bump version i ``package.json`` og ``NEWS.rst`` iht. Semantic Versioning. Inden første major, skal major ikke løftes selv ved API brud.

* Byg og commit ny udgave af Vuedoc.

* Verificer med Alex at release notes (NEWS.rst) er korrekte ift. Redmine.

* Test og verificer at release ikke indeholder breaking bugs, e.g. på ``moratest.atlas.magenta.dk``

* Opret PR fra release branch til ``master`` (Reviewet af denne skal udelukkende forkusere på de få ændringer der er foretaget i forbindelse med release, e.g. bumping af version og ændring af dato i release notes.)

* 'Draft new release' på Github. Sæt tag version og release title til versionen fra ``package.json``. Indsæt gældende release notes fra ``NEWS.rst`` i description. Formatteringen skal muligvis tilpasses lidt for at fungere med Githubs Markdown.

* Opret PR fra release branch til ``development``. Slet release branch.

