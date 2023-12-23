from __future__ import annotations
from asyncpg import Record
from attr import dataclass
from mautrix.types import RoomID
from mautrix.util.async_db import Database, Scheme

@dataclass
class Subscription:
	room_id: RoomID
	fest_start: bool
	bigrun_start: bool
	event_start: bool

	@classmethod
	def from_row(cls, row: Record | None) -> Subscription | None:
		if not row:
			return None
		room_id = row["room_id"]
		if not room_id:
			return None
		fest_start = bool(row["fest_start"])
		bigrun_start = bool(row["bigrun_start"])
		event_start = bool(row["event_start"])
		return cls(
			room_id=room_id,
			fest_start=fest_start,
			bigrun_start=bigrun_start,
			event_start=event_start
		)

class DBManager:
	db: Database
	
	def __init__(self, db: Database) -> None:
		self.db = db

	async def getSubscriptions(self) -> list[Subscription]:
		q = """
		SELECT room_id, fest_start, bigrun_start, event_start
		FROM subscription
		"""
		rows = await self.db.fetch(q)
		return list(map(lambda row: Subscription.from_row(row), rows))


	async def getSubscription(self, roomId: RoomID) -> Subscription:
		q = """
		SELECT room_id, fest_start, bigrun_start, event_start
		FROM subscription
		WHERE room_id = $1
		"""
		row = await self.db.fetchrow(q, roomId)
		return Subscription.from_row(row)

	async def subscribe(self, roomId: RoomID, festStart: bool = False, bigRunStart: bool = False, eventStart: bool = False) -> None:
		oldSub = await self.getSubscription(roomId)
		if oldSub:
			q = """
			UPDATE subscription SET fest_start = $2, bigrun_start = $3, event_start = $4 WHERE room_id = $1
			"""
		else:
			q = """
			INSERT INTO subscription (room_id, fest_start, bigrun_start, event_start)
			VALUES ($1, $2, $3, $4)
			"""
		await self.db.execute(q, roomId, festStart, bigRunStart, eventStart)

	async def unsubscribe(self, roomId: RoomID) -> None:
		q = "DELETE FROM subscription WHERE room_id = $1"
		await self.db.execute(q, roomId)

	async def updateRoomId(self, old: RoomID, new: RoomID) -> None:
		await self.db.execute("UPDATE subscription SET room_id = $1 WHERE room_id = $2", new, old)