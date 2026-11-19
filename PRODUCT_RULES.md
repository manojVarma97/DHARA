# Dhara product and delivery rules

- Catalogue prices are stored as integer paise in PostgreSQL.
- Free delivery applies only to `VZM`, `Vizianagaram`, or `Vizianagaram Urban` as configured in the starter.
- All other cities require a configured delivery fee. Until the owner confirms the fee, checkout is blocked with a clear error.
- Four delivery windows are seeded; capacity is 20 orders per slot/day by default.
- Update `database/init.sql` for a fresh database, or update rows directly for an existing database.
- Before public launch, confirm whether 20L cans have deposits/returns, minimum order quantities, serviceable pin codes, taxes, cancellation rules and delivery fees.
