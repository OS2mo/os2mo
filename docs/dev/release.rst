Release procedure
=================
* Create a release branch for the release, according to GitFlow, e.g. ``release/1.0.0``

* Bump the version in ``package.json`` and ``NEWS.rst`` according to Semantic Versioning. Prior to the first major version, the major version shouldn't be bumped even in the case of incompatible API changes.

* Build and commit a new version of the Vuedoc-generated documentation.

* Verify with Alex (or whoever else is in charge), that the release notes in ``NEWS.rst`` are up-to-date wrt. Redmine.

* Test the release, and verify that it doesn't contain any breaking bugs or regressions.

* Create a pull request from the release branch to ``master``. The review should focus primarily on the few changes made during the release process, e.g. bumping the version and finalizing the release notes. All other changes have already gone through review once. Do not delete the release branch yet!

* Select 'Draft new release' on Github. Select ``master`` as target. Set the tag version and release title to the version from ``package.json``. Insert relevant release notes from ``NEWS.rst`` in the description. The formatting might need minor adjustments to conform to GitHub's Markdown. 

* Finally, create a pull request from the release branch to ``development``. Delete the release branch.

You did it. 🎈

