from mautrix.util.async_db import Connection, Scheme, UpgradeTable

upgrade_table = UpgradeTable()

@upgrade_table.register(description="Subscription database")
async def upgrade_v1(conn: Connection) -> None:
	await conn.execute(
		f"""CREATE TABLE IF NOT EXISTS subscription (
			room_id TEXT NOT NULL,

			fest_start BOOLEAN DEFAULT false,
			bigrun_start BOOLEAN DEFAULT false,
			event_start BOOLEAN DEFAULT false,

			PRIMARY KEY (room_id)
		)"""
	)