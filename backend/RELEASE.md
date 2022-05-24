Release type: minor

[#49535] Fix a permanent redirect in users browsers for our old saml SSO.

This works by redirecting back to the initial redirect path (/), and thus
triggering a redirect cycle in the browser, which in effect makes the browser
try to fetch the initial redirect path, thus clearing the permanent redirect.
