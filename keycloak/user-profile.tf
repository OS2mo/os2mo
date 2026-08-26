# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
#
# Keycloak 24+ filters user attributes not declared in the realm's user
# profile. Declare all default attributes plus `object-guid` so the
# realm-builder can set them on users.

resource "keycloak_realm_user_profile" "mo_user_profile" {
  realm_id = keycloak_realm.mo.id

  attribute {
    name         = "username"
    display_name = "$${username}"
    validator {
      name = "length"
      config = {
        min = "3"
        max = "255"
      }
    }
    validator {
      name = "username-prohibited-characters"
    }
    validator {
      name = "up-username-not-idn-homograph"
    }
    permissions {
      view = ["admin", "user"]
      edit = ["admin", "user"]
    }
  }

  attribute {
    name         = "email"
    display_name = "$${email}"
    validator {
      name = "email"
    }
    validator {
      name = "length"
      config = {
        max = "255"
      }
    }
    required_for_roles = ["user"]
    permissions {
      view = ["admin", "user"]
      edit = ["admin", "user"]
    }
  }

  attribute {
    name         = "firstName"
    display_name = "$${firstName}"
    validator {
      name = "length"
      config = {
        max = "255"
      }
    }
    validator {
      name = "person-name-prohibited-characters"
    }
    required_for_roles = ["user"]
    permissions {
      view = ["admin", "user"]
      edit = ["admin", "user"]
    }
  }

  attribute {
    name         = "lastName"
    display_name = "$${lastName}"
    validator {
      name = "length"
      config = {
        max = "255"
      }
    }
    validator {
      name = "person-name-prohibited-characters"
    }
    required_for_roles = ["user"]
    permissions {
      view = ["admin", "user"]
      edit = ["admin", "user"]
    }
  }

  attribute {
    name         = "object-guid"
    display_name = "object-guid"
    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }
}
