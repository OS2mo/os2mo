#Overview

`/o`

`/o/<uuid>`

`/o/<uuid>/children`

`/ou/<uuid>`

`/ou/<uuid>/children`

`/ou/<uuid>/history`

`/ou/<uuid>/details`

`/ou/<uuid>/details/<detail_name>`

`/ou/create`

`/ou/<uuid>/edit`

`/ou/<uuid>/terminate`

`/e`

`/e/<uuid>`

`/e/<uuid>/details`

`/e/<uuid>/detail/<detail_name>`

`/e/<uuid>/history`

`/e/<uuid>/create`

`/e/<uuid>/edit`

`/e/<uuid>terminate`

`/f`

`/f/<facet_name>`

`/search?q=<query>`

`/auth/login`

`/auth/logout`

#Organisation

##Get all organisations

`GET /o`

Return a list of all organisations

**RESPONSE**

```json
[
	{
		uuid:  <uuid>
		name: <String>
		has_children: <Boolean>
	},
	...
]
```

##Get organisation

`GET /o/<uuid>`

Return stats about the organisation

**RESPONSE**

```json
{
	uuid: <uuid>
	name: <String>
	employees: <int>
	units: <int>
	...
}
```

##Get organisation children

`GET /o/<uuid>/children`

Return a list of children for an organisation

**RESPONSE**

```json
{
	uuid:  <uuid>
	name: <String>
	children: [
		{
			uuid: <uuid>
			name: <String>
			has_children: <Boolean>
		},
		...
	]
}
```

#Organisation unit

##Get organisation unit

`GET /ou/<uuid>`

Return basic info about an organisation unit

**RESPONSE**

```json
{
	uuid: <uuid>
	name: <String>
	organisation: <organisation object>
	parent: <parent_org_unit object>
	type: <type object>
	valid_from: <ISO8601>
	valid_to: <ISO8601>
}
```

##Get organisation unit children

`GET /ou/<uuid>/children`

Return a list of children for an organisation unit

**RESPONSE**

```json
{
	uuid:  <uuid>
	name: <String>
	children: [
		{
			uuid: <uuid>
			name: <String>
			has_children: <Boolean>
		},
		...
	]
}
```

##Get organisation unit history

`GET /ou/<uuid>/history`

Return a list of all changes on the organisation unit

**RESPONSE**

```json
[
	{
		uuid:  <uuid>
		date: <ISO8601>
		section: <section object>
		object: <object object>
		action: <action object>
		valid_from: <ISO8601>
		user: {
			uuid: <uuid>
			name: <String>
		}
	},
	...
]
```

##Get available organisation unit details

`GET /ou/<uuid>/details`

```json
{
	unit: <Boolean>
	location: <Boolean>
	contact_channel: <Boolean>
	engagements: <Boolean>
	...
}
```

##Get organisation unit unit details

`GET /ou/<uuid>/details/unit`

**RESPONSE**

```json
{
	present: [
		{
			uuid: <uuid>
			name: <String>
			unit_type: <unit_type object>
			org_unit: <org_unit object>
			valid_from: <ISO8601>
			valid_to: <ISO8601>
		},
		...
	]
	past: [...]
	future: [...]
}
```

##Get organisation unit `type` details

`GET /ou/<uuid>/details/location`

`GET /ou/<uuid>/details/contact_channel`

`GET /ou/<uuid>/details/engagements`

##Create a new organisation unit

`POST /ou/create`

Create a new organisation unit

**REQUEST OBJECT**

```json
{
	//to be determined
}
```

**RESPONSE**

```json
{
	//to be determined
}
```

#Edit an organisation unit

`POST /ou/<uuid>/edit`

Edit an organisation unit

**REQUEST OBJECT**

```json
{
	//to be determined
}
```

**RESPONSE**

```json
{
	//to be determined
}
```

#Terminate an organisation unit

`DELETE /ou/<uuid>/terminate`

**REQUEST OBJECT**

```json
{
	valid_from: <ISO8601>
}
```

**RESPONSE**

```json
{
	//to be determined
}
```

#Employees

##Get all employees

`GET /e`

Return a list of all employees

```json
[
	{
		uuid: <uuid>
		name: <String>
	},
	...
]
```

##Get employee

`GET /e/<uuid>`

Return an employee

```json
{
	uuid: <uuid>
	name: <String>
	cpr_no: <int>
}
```

##Get available employee details

`GET /e/<uuid>/details`

Return a list of details available for an employee

```json
{
	engagement: <Boolean>
	association: <Boolean>
	it: <Boolean>
	contact: <Boolean>
	...
}
```

##Get employee engagement details

`GET /e/<uuid>/details/engagement`

Get a list of all engagement details for an employee

```json
{
	present: [
		{
			uuid: <uuid>
			org_unit: <org_unit object>
			job_function: <job_function object>
			engagement_type: <engagement_type object>
			valid_from: <ISO8601>
			valid_to: <ISO8601>
		},
		...
	]
	past: [...]
	future: [...]
}
```

##Get employee `type` details

`GET /e/<uuid>/details/association`

`GET /e/<uuid>/details/it`

`GET /e/<uuid>/details/contact`

##Get employee history

`GET /e/<uuid>/history`

Return a list of all changes on the employee

```json
[
	{
		uuid: <uuid>
		date: <ISO8601>
		section: <section object>
		object: <object object>
		action: <action object>
		valid_from: <ISO8601>
		user: {
			uuid: <uuid>
			name: <String>
		}
	},
	...
]
```

##Create a new employee employment
`POST /e/<uuid>/create`

Create a new employment

**REQUEST OBJECT**

```json
[
	{
		type: engagement
		org_unit_uuid: <uuid>
		job_title_uuid: <uuid>
		engagement_type_uuid: <uuid>
		valid_from: <ISO8601>
		valid_to: <ISO8601>
	},
	{
		type: associaton
		...
	},
	{
		type: it
		...
	},
	...
]
```

**RESPONSE**

```json
{
	//to be determined
}
```

##Edit employee details

`POST /e/<uuid>/edit`

Edit an employee

*REQUEST OBJECT*

```json
[
	{
		type: engagement
		uuid: <uuid>
	},
	{
		type: move,
		destination_uuid: <uuid>
		valid_from: <ISO8601>
		valid_to: <ISO8601>
	},
	{
		type: contact,
		channel_uuid: <uuid>
		value: <String>
		valid_from: <ISO8601>
		valid_to: <ISO8601>
	}
]
```

*RESPONSE*

```json
{
	//to be determined
}
```

##Terminate an employee


`DELETE /e/<uuid>/terminate`

Terminate an employee

*REQUEST OBJECT*

```json
{
	valid_from: <ISO8601>
}
```

*RESPONSE*

```json
{
	//to be determined
}
```

#Facets

##Get a list of all facets

`GET /f`

Get a list of all facets

*RESPONSE*

```json
[
	{
		name: org_unit_types
	},
	{
		name: contact_types
	},
	...
]
```

##Get `facet_name` facets

`GET /f/<facet_name>`

Get a list containing the facet values

*RESPONSE*

```json
[
	{
		name: <String>
		uuid: <uuid>
	},
	...
]
```

#Search

`GET /search?q=<query>`

Return a list of results based on the query

It should be able to return both organisations and employees

```json
[
	{
		type: employee
		name: <String>
		uuid: <uuid>
	},
	{
		type: organisation
		name: <String>
		uuid: <uuid>
	}
]
```

#Authentication

##Login

`POST /auth/login`

**POST OBJECT**

```json
{
	username: <String>
	password: <String>
	remember_me: <Boolean>
}
```

**RESPONSE**

```json
{
	//to be determined
}
```

##Logout

`POST /auth/logout`

**POST PBJECT**

```json
{
	username: <String>
}
```

**RESPONSE**

```json
{
	//to be determined
}
```
