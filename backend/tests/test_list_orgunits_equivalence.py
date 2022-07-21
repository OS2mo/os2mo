from more_itertools import unzip

from mora import common

async def list_orgunits(
    orgid: UUID,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    query: Optional[str] = None,
    root: Optional[str] = None,
    hierarchy_uuids: Optional[List[UUID]] = Query(default=None),
    only_primary_uuid: Optional[bool] = None,
):
    orgid = str(orgid)
    c = common.get_connector()

    kwargs = dict(
        limit=limit,
        start=start,
        tilhoerer=orgid,
        gyldighed="Aktiv",
    )

    if query:
        kwargs.update(vilkaarligattr="%{}%".format(query))
    if hierarchy_uuids:
        kwargs["opmærkning"] = [str(uuid) for uuid in hierarchy_uuids]

    uuid_filters = []
    if root:
        enheder = await c.organisationenhed.get_all()

        uuids, enheder = unzip(enheder)
        # Fetch parent_uuid from objects
        parent_uuids = map(mapping.PARENT_FIELD.get_uuid, enheder)
        # Create map from uuid --> parent_uuid
        parent_map = dict(zip(uuids, parent_uuids))

        def entry_under_root(uuid):
            """Check whether the given uuid is in the subtree under 'root'.

            Works by recursively ascending the parent_map.

            If the specified root is found, we must have started in its subtree.
            If the specified root is not found, we will stop searching at the
                root of the organisation tree.
            """
            if uuid not in parent_map:
                return False
            return uuid == root or entry_under_root(parent_map[uuid])

        uuid_filters.append(entry_under_root)

    details = get_details_from_query_args(util.get_query_args())

    async def get_minimal_orgunit(*args, **kwargs):
        return await get_one_orgunit(
            *args, details=details, only_primary_uuid=only_primary_uuid, **kwargs
        )

    search_result = await c.organisationenhed.paged_get(
        get_minimal_orgunit, uuid_filters=uuid_filters, **kwargs
    )
    return search_result


