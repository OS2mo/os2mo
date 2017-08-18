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
16) Test that search is working (with and without wildcards)
17) Check that it is not possible to create an org unit with an invalid date range
18) Check that it is not possible to move an org unit to its own subtree
19) Check that the "History" button is working

Testing temporality
-------------------
Wipe the DB and use the spreadsheet found in ``sandbox/AAK/AARHUS_3orgUnits.xlsx`` to
test the following (or just make a similar scenario on the LoRa instance, you
have running). Check that you can construct the following temporal org unit
configuration. Begin by setting the org unit name and 'overordnet' as::

  -----------[--------n1--------)[-----n2-----)[---------n3-------------
  -----------[-------------------------o1-------------------------------

where ``n`` refers to the name and ``o`` refers to 'overordnet'. Then set the
org unit 'overordnet' as::

  -----------[----o1---)[--------------o2------------------)[---o1------

and check that the resulting configuration::

  -----------[--n1,o1--)[-n1,o2-)[---n2,o2----)[-n3,o2-----)[---n3,o1---

is shown correctly in the frontend.

Also test that it is possible to add a new location in the past and a new
location in the future for the same org unit.