## What does this MR do?
<!--
Briefly describe what this MR is about.
Examples:
 Implements feature X
 Fixes bug in Y
-->


## Author's checklist

- [ ] The code has been rebased/squashed into a minimal amount of atomic commits that reference the ticket ID (eg. `[#12345] Implement featureX in Y`)
- [ ] The title of this MR contains the relevant ticket no., formatted like `[#12345]` or `#12345`
- [ ] The release notes (``NEWS.rst``) have been updated
- [ ] If the feature introduces changes relevant to the deployment process (new configuration, etc.), I have added a note to the ``NEWS.rst`` detaling what is updated/changed
- [ ] The corresponding Redmine ticket has been set to `Needs review`
- [ ] The Redmine ticket has a link to this MR
- [ ] I have added tests or made a conscious decision not to
- [ ] I have updated the documentation or made a conscious decision not to
- [ ] If an interface has changed, I have discussed it with all users of said interface

## Review checklist

- [ ] The code is understandable, well-structured and sufficiently documented
- [ ] I would be able to deploy this feature and verify that it's working without further input from the author

## Pre-merge checklist

- [ ] If the feature introduces changes relevant to the deployment process, Redmine tickets have been created
- [ ] If this change affects the development workflow, I have notified other developers by email or chat.

