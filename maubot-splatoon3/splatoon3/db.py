from __future__ import annotations
from asyncpg import Record
from attr import dataclass
from mautrix.types import RoomID
from mautrix.util.async_db import Database, Scheme

@dataclass
class Subscription:
	room_id: RoomID
	fest_soon: bool
	fest_start: bool
	bigrun_start: bool
	event_start: bool
	event_happen: bool

	@classmethod
	def from_row(cls, row: Record | None) -> Subscription | None:
		if not row:
			return None
		room_id = row["room_id"]
		if not room_id:
			return None
		fest_soon = bool(row["fest_soon"])
		fest_start = bool(row["fest_start"])
		bigrun_start = bool(row["bigrun_start"])
		event_start = bool(row["event_start"])
		event_happen = bool(row["event_happen"])
		return cls(
			room_id=room_id,
			fest_soon=fest_soon,
			fest_start=fest_start,
			bigrun_start=bigrun_start,
			event_start=event_start,
			event_happen=event_happen
		)

@dataclass
class PastFest:
	fest_id: str
	start_time: str
	reported: bool

	@classmethod
	def from_row(cls, row: Record | None) -> PastFest | None:
		if not row:
			return None
		fest_id = row["fest_id"]
		if not fest_id:
			return None
		start_time = row["start_time"]
		if not start_time:
			return None
		reported = bool(row["reported"])
		return cls(
			fest_id=fest_id,
			start_time=start_time,
			reported=reported
		)

class DBManager:
	db: Database
	
	def __init__(self, db: Database) -> None:
		self.db = db

	async def getSubscriptions(self) -> list[Subscription]:
		q = """
		SELECT room_id, fest_start, bigrun_start, event_start, event_happen, fest_soon
		FROM subscription
		"""
		rows = await self.db.fetch(q)
		return list(map(lambda row: Subscription.from_row(row), rows))


	async def getSubscription(self, roomId: RoomID) -> Subscription:
		q = """
		SELECT room_id, fest_start, bigrun_start, event_start, event_happen, fest_soon
		FROM subscription
		WHERE room_id = $1
		"""
		row = await self.db.fetchrow(q, roomId)
		return Subscription.from_row(row)

	async def subscribe(self, roomId: RoomID, festStart: bool = False, bigRunStart: bool = False, eventStart: bool = False, eventHappen: bool = False, festSoon: bool = False) -> None:
		oldSub = await self.getSubscription(roomId)
		if oldSub:
			q = """
			UPDATE subscription SET fest_start = $2, bigrun_start = $3, event_start = $4, event_happen = $5, fest_soon = $6 WHERE room_id = $1
			"""
		else:
			q = """
			INSERT INTO subscription (room_id, fest_start, bigrun_start, event_start, event_happen, fest_soon)
			VALUES ($1, $2, $3, $4, $5, $6)
			"""
		await self.db.execute(q, roomId, festStart, bigRunStart, eventStart, eventHappen, festSoon)

	async def unsubscribe(self, roomId: RoomID) -> None:
		q = "DELETE FROM subscription WHERE room_id = $1"
		await self.db.execute(q, roomId)

	async def updateRoomId(self, old: RoomID, new: RoomID) -> None:
		await self.db.execute("UPDATE subscription SET room_id = $1 WHERE room_id = $2", new, old)

	async def getPastFests(self) -> list[PastFest]:
		q = """
		SELECT fest_id, start_time, reported
		FROM past_fest
		"""
		rows = await self.db.fetch(q)
		return list(map(lambda row: PastFest.from_row(row), rows))

	async def addFest(self, fest_id: str, start_time: str, reported: bool = False) -> None:
		q = """
		INSERT INTO past_fest (fest_id, start_time, reported)
		VALUES ($1, $2, $3)
		"""
		await self.db.execute(q, fest_id, start_time, reported)
	
	async def markFestReported(self, fest_id: str) -> None:
		q = """
		UPDATE past_fest
		SET reported = $2
		WHERE fest_id = $1
		"""
		await self.db.execute(q, fest_id, True)
