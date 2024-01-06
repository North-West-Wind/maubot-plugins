from mautrix.util.async_db import Connection, Scheme, UpgradeTable

upgrade_table = UpgradeTable()

@upgrade_table.register(description="Subscription database")
async def upgrade_v1(conn: Connection, scheme: Scheme) -> None:
	gen = "GENERATED ALWAYS AS IDENTITY" if scheme != Scheme.SQLITE else ""
	await conn.execute(
		f"""CREATE TABLE IF NOT EXISTS subscription (
			id INTEGER {gen},
			room_id TEXT NOT NULL,

			fest_start BOOLEAN DEFAULT false,
			bigrun_start BOOLEAN DEFAULT false,
			event_start BOOLEAN DEFAULT false,

			PRIMARY KEY (id)
		)"""
	)

@upgrade_table.register(description="event_happen events for subscription")
async def upgrade_v2(conn: Connection) -> None:
	await conn.execute("ALTER TABLE subscription ADD COLUMN event_happen BOOLEAN DEFAULT false")

@upgrade_table.register(description="fest_soon event for subscription")
async def upgrade_v3(conn: Connection, scheme: Scheme) -> None:
	await conn.execute("ALTER TABLE subscription ADD COLUMN fest_soon BOOLEAN DEFAULT false")
	gen = "GENERATED ALWAYS AS IDENTITY" if scheme != Scheme.SQLITE else ""
	await conn.execute(
		f"""CREATE TABLE IF NOT EXISTS past_fest (
			id INTEGER {gen},
			fest_id TEXT NOT NULL,
			start_time TEXT NOT NULL,
			reported BOOLEAN DEFAULT false,

			PRIMARY KEY (id)
		)"""
	)