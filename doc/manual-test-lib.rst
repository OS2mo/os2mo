Manual testing of MO
====================

Before merging a branch into master, check that the following is ok. This is
not a complete test of all features, but just some quick tests to check
that all the major features are not unexpectedly broken.

Remember to check that everything looks ok (maybe also directly in LoRa)
after each of the following steps:

1) Create an org unit without specifying an enddate
2) Create an org unit with a final enddate
3) End the org unit created in 1)
4) End the org unit again with a date later than the enddate from 3)
5) Move the org unit created in 1) to beneath the org unit from 2) (with immediate effect)
6) Rename the org unit created in 1) (with immediate effect)
7) Add a contact channel to the org unit from 1) (with immediate effect)
8) Add two more contact channels to the org unit from 1) (with immediate effect)
9) Add another location (not primary address) to the org unit from 1) (with immediate effect)
10) Add another location (primary address) to the org unit from 1) (with immediate effect)
11) Change the address of the just added location (with immediate effect)
12) TODO: more editing of locations and contact
13) Edit the org unit from 1) by changing the unit type - leave the date unchanged
14) Edit the org unit from 1) by changing the org unit startdate (i.e. 'gyldighed')
15) Edit both the unit type and the org unit startdate in one go (for the org unit from 1))

