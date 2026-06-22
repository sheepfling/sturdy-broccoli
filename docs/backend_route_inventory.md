# Backend Route Inventory

This page is the hub for the backend route story.

It covers both Python RTI implementation lanes:

- the 2010 Python RTI centered on `hla-backend-inmemory`
- the main full 2025 Python RTI centered on `hla-backend-python2025`

It also keeps the architectural boundary explicit:

- `hla-backend-python2025` is the main `rti1516_2025` implementation lane
- `hla-backend-shim` is only a compatibility-wrapper alias over that lane
- Java/C++ binding routes are route surfaces, not separate Python RTIs

Use it when you need to answer:

- which backend routes exist at all
- which routes are direct versus transport-hosted
- where the evidence and command references live

For the current 2025 proof path, treat these as the primary route identities:

- `python-2025-inprocess`: direct executable evidence over the main
  `hla-backend-python2025` RTI lane
- `python-2025-fedpro-grpc`: bounded hosted route evidence over that same RTI
  lane, not a separate 2025 runtime family

Canonical order:

1. route inventory
2. baseline attribution
3. remote transport routes
4. test commands
5. what is not claimed

Internal index:

- [backend_route_inventory_routes.md](backend_route_inventory_routes.md)
- [backend_route_inventory_baselines.md](backend_route_inventory_baselines.md)
- [backend_route_inventory_remote.md](backend_route_inventory_remote.md)
- [backend_route_inventory_commands.md](backend_route_inventory_commands.md)

Use this page when you want the route story without the full matrix detail.
