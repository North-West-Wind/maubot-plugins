from datetime import datetime, timezone
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event
from maubot.matrix import parse_formatted
from mautrix.types import EventType, Format, StateEvent, TextMessageEventContent
from mautrix.util.async_db import UpgradeTable
import pytz
import schedule
from .db import DBManager
from .migrations import upgrade_table

# remind you that i'm a javascript programmer
class dotdict(dict):
  # dot.notation access to dictionary attributes
	# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
	def __getattr__(*args):
		val = dict.get(*args)
		if type(val) is dict:
			return dotdict(val)
		if type(val) is list:
			return list(map(lambda x: dotdict(x) if type(x) is dict else x, val))
		return val
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class Splatoon3Plugin(Plugin):
	dbm: DBManager

	@classmethod
	def get_db_upgrade_table(cls) -> UpgradeTable:
		return upgrade_table

	async def start(self) -> None:
		await super().start()
		self.dbm = DBManager(self.database)
		schedule.every().hour.at(":00", pytz.timezone('UTC')).do(self.rotationUpdate)

	@command.new(help="Shows you the current rotation.", require_subcommand=False)
	async def splatoon3(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "**Current rotation:**"
		if data.regularSchedules.nodes[0].regularMatchSetting:
			setting = data.regularSchedules.nodes[0].regularMatchSetting
			description += "  \nTurf War: " + self._stages_str(setting.vsStages)
		if data.bankaraSchedules.nodes[0].bankaraMatchSettings:
			setting = data.bankaraSchedules.nodes[0].bankaraMatchSettings[0]
			description += "  \n" + setting.vsRule.name + " (Series): " + self._stages_str(setting.vsStages)
			setting = data.bankaraSchedules.nodes[0].bankaraMatchSettings[1]
			description += "  \n" + setting.vsRule.name + " (Open): " + self._stages_str(setting.vsStages)
		if data.xSchedules.nodes[0].xMatchSetting:
			setting = data.xSchedules.nodes[0].xMatchSetting
			mode = data.xSchedules.nodes[0].xMatchSetting.vsRule.name
			description += "  \n" + setting.vsRule.name + " (X): " + self._stages_str(setting.vsStages)
		if data.currentFest:
			# todo when splatfest happens
			pass
		if data.festSchedules.nodes[0].festMatchSettings:
			setting = data.festSchedules.nodes[0].festMatchSettings[0]
			description += "  \nSplatfest (Open): " + self._stages_str(setting.vsStages)
			setting = data.festSchedules.nodes[0].festMatchSettings[1]
			description += "  \nSplatfest (Pro): " + self._stages_str(setting.vsStages)
		
		coopSchedule = data.coopGroupingSchedule
		if len(coopSchedule.regularSchedules.nodes) > 0:
			setting = coopSchedule.regularSchedules.nodes[0].setting
			description += "\n\n**Salmon Run:**  \n" + setting.coopStage.name + " | " + setting.boss.name + "  \n"
			description += " / ".join(map(lambda w: w.name, setting.weapons))
		if len(coopSchedule.bigRunSchedules.nodes) > 0:
			# todo when big run happens
			pass
		if len(coopSchedule.teamContestSchedules.nodes) > 0:
			# todo when eggstra work happens
			pass

		nextChallengeTime = data.eventSchedules.nodes[0].timePeriods[0]
		challengeName = data.eventSchedules.nodes[0].leagueMatchSetting.leagueMatchEvent.name
		description += "\n\n**" + challengeName + "** "
		if datetime.fromisoformat(nextChallengeTime.startTime) <= datetime.utcnow().replace(tzinfo=timezone.utc) <= datetime.fromisoformat(nextChallengeTime.endTime):
			description += "is happening right now!"
		else:
			description += "will happen on " + self._iso_str(nextChallengeTime.startTime) + " (UTC+00:00)"
		description += "  \n*" + data.eventSchedules.nodes[0].leagueMatchSetting.leagueMatchEvent.desc + "*"
		description += "  \n" + self._stages_str(data.eventSchedules.nodes[0].leagueMatchSetting.vsStages)

		await evt.reply(description)

	@splatoon3.subcommand("turf", help="Shows you the schedule of Turf War.")
	async def turf(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		hasFest = False
		for ii, node in enumerate(data.regularSchedules.nodes):
			if not node.regularMatchSetting:
				if not hasFest:
					hasFest = True
					description += "  \nLooks like a Splatfest is happening!"
				continue
			description += "\n\n"
			if ii == 0:
				description += "**Now**"
			else:
				description += "**" + self._iso_str(node.startTime) + "**"
			description += "  \n" + self._stages_str(node.regularMatchSetting.vsStages)
		await evt.reply(description)

	@splatoon3.subcommand("anarchy", help="Shows you the schedules of Anarchy Battle.")
	async def anarchy(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		hasFest = False
		for ii, node in enumerate(data.bankaraSchedules.nodes):
			if not node.bankaraMatchSettings:
				if not hasFest:
					hasFest = True
					description += "  \nLooks like a Splatfest is happening!"
				continue
			description += "\n\n"
			if ii == 0:
				description += "**Now**"
			else:
				description += "**" + self._iso_str(node.startTime) + "**"
			description += "  \n" + self._stages_str(node.bankaraMatchSettings[0].vsStages)
			description += " **" + node.bankaraMatchSettings[0].vsRule.name + "**"
			description += "  \n" + self._stages_str(node.bankaraMatchSettings[1].vsStages)
			description += " **" + node.bankaraMatchSettings[1].vsRule.name + "**"
		await evt.reply(description)

	@splatoon3.subcommand("x", help="Shows you the schedule of X Battle.")
	async def x(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		hasFest = False
		for ii, node in enumerate(data.xSchedules.nodes):
			if not node.xMatchSetting:
				if not hasFest:
					hasFest = True
					description += "  \nLooks like a Splatfest is happening!"
				continue
			description += "\n\n"
			if ii == 0:
				description += "**Now**"
			else:
				description += "**" + self._iso_str(node.startTime) + "**"
			description += "  \n" + self._stages_str(node.xMatchSetting.vsStages)
			description += " **" + node.xMatchSetting.vsRule.name + "**"
		await evt.reply(description)

	@splatoon3.subcommand("fest", help="Shows you the schedules of Splatfest Battle.")
	async def fest(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		if data.currentFest:
			# todo when splatfest happens
			pass
		hasFest = False
		for ii, node in enumerate(data.festSchedules.nodes):
			if node.festMatchSettings:
				if not hasFest:
					hasFest = True
				description += "\n\n"
				if ii == 0:
					description += "**Now**"
				else:
					description += "**" + self._iso_str(node.startTime) + "**"
				description += "  \n" + self._stages_str(node.festMatchSettings[0].vsStages)
				description += " **" + node.festMatchSettings[0].vsRule.name + "**"
				description += "  \n" + self._stages_str(node.festMatchSettings[1].vsStages)
				description += " **" + node.festMatchSettings[1].vsRule.name + "**"
		if not hasFest:
			description += "  \nIt doesn't look like there's any Splatfest battle soon."
		await evt.reply(description)

	@splatoon3.subcommand("salmon", help="Shows you the schedule of Salmon Run.")
	async def salmon(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		for ii, node in enumerate(data.coopGroupingSchedule.regularSchedules.nodes):
			description += "\n\n**" + self._iso_str(node.startTime) + " - " + self._iso_str(node.endTime) + "**"
			if ii == 0:
				if datetime.fromisoformat(node.startTime) < datetime.utcnow().replace(tzinfo=timezone.utc) < datetime.fromisoformat(node.endTime):
					description += " **(Now!)**"
			description += "  \n" + node.setting.coopStage.name + " | " + node.setting.boss.name
			description += "  \n" + " / ".join(map(lambda w: w.name, node.setting.weapons))
		await evt.reply(description)

	@splatoon3.subcommand("challenge", help="Shows you the schedule of Challenge.")
	async def challenge(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "Note: The times are in UTC+00:00"
		for ii, node in enumerate(data.eventSchedules.nodes):
			description += "\n# " + node.leagueMatchSetting.leagueMatchEvent.name + "\n"
			description += node.leagueMatchSetting.leagueMatchEvent.desc + "\n\n"
			description += node.leagueMatchSetting.leagueMatchEvent.regulation + "\n\n"
			description += "**" + self._iso_str(node.timePeriods[0].startTime) + " - " + self._iso_str(node.timePeriods[-1].endTime) + "**"
			if ii == 0:
				if self._is_now_between_isos(node.timePeriods[0].startTime, node.timePeriods[-1].endTime):
					description += " **(Now!)**"
			description += "  \n" + self._stages_str(node.leagueMatchSetting.vsStages) + " **" + node.leagueMatchSetting.vsRule.name + "**"
		await evt.reply(description, allow_html=True)

	@splatoon3.subcommand("subscribe", help="Get notified when special events start. You can pass multiple arguments at once. Omitting arguments will unsubscribe the room from notifications. Valid events: festStart, bigRunStart, challengeStart")
	@command.argument("events", required=False, pass_raw=True)
	async def subscribe(self, evt: MessageEvent, events: str) -> None:
		festStart = False
		bigRunStart = False
		eventStart = False
		for arg in events.split():
			match arg:
				case "festStart":
					festStart = True
				case "bigRunStart":
					bigRunStart = True
				case "challengeStart":
					eventStart = True
		await self.dbm.subscribe(evt.room_id, festStart, bigRunStart, eventStart)
		description = "Subscribed to "
		if (not festStart) and (not bigRunStart) and (not eventStart):
			description += "nothing."
		else:
			things = list()
			if festStart:
				things.append("**Splatfest Start**")
			if bigRunStart:
				things.append("**Big Run Start**")
			if eventStart:
				things.append("**Challenge Start**")
			description += ", ".join(things)
		await evt.reply(description)
	
	@splatoon3.subcommand("subscriptions", help="Check subscriptions of this room.")
	async def subscriptions(self, evt: MessageEvent) -> None:
		sub = await self.dbm.getSubscription(evt.room_id)
		festStart = sub.fest_start if sub else False
		bigRunStart = sub.bigrun_start if sub else False
		eventStart = sub.event_start if sub else False
		description = "This room is subscribed to "
		if (not festStart) and (not bigRunStart) and (not eventStart):
			description += "nothing."
		else:
			things = list()
			if festStart:
				things.append("**Splatfest Start**")
			if bigRunStart:
				things.append("**Big Run Start**")
			if eventStart:
				things.append("**Challenge Start**")
			description += ", ".join(things)
		await evt.reply(description)

	@event.on(EventType.ROOM_TOMBSTONE)
	async def tombstone(self, evt: StateEvent) -> None:
		if not evt.content.replacement_room:
			return
		self.dbm.updateRoomId(evt.room_id, evt.content.replacement_room)

	async def rotationUpdate(self) -> None:
		if datetime.now().hour % 2:
			# hour is odd. no update
			return
		self.log.debug("Checking rotation at " + datetime.now().strftime("%m/%d %H:%M"))
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		challengeStr = ""
		node = data.eventSchedules.nodes[0]
		if len(node.timePeriods) == 6:
			if self._is_now_between_isos(node.timePeriods[0].startTime, node.timePeriods[0].endTime):
				challengeStr = f"# {node.leagueMatchSetting.leagueMatchEvent.name}"
				challengeStr += "\nis happening right now!  \n"
				challengeStr += node.leagueMatchSetting.leagueMatchEvent.desc + "\n\n"
				challengeStr += node.leagueMatchSetting.leagueMatchEvent.regulation + "\n\n"
				challengeStr += "**" + self._iso_str(node.timePeriods[0].startTime) + " - " + self._iso_str(node.timePeriods[-1].endTime) + "**"
				challengeStr += "  \n" + self._stages_str(node.leagueMatchSetting.vsStages) + " **" + node.leagueMatchSetting.vsRule.name + "**"
		# todo make festStr and bigRunStr when splatfest or big run happens
		festStr = ""
		bigRunStr = ""
		subs = await self.dbm.getSubscriptions()
		for sub in subs:
			if challengeStr and sub.event_start:
				content = TextMessageEventContent(msgtype=MessageType.NOTICE, body=challengeStr)
				content.format = Format.HTML
				content.body, content.formatted_body = await parse_formatted(
					content.body, render_markdown=True, allow_html=True
				)
				await self.client.send_message_event(sub.room_id, EventType.ROOM_MESSAGE, content)

	def _stages_str(self, vsStages: list[dotdict]) -> str:
		return " | ".join(map(lambda x: x.name, vsStages))

	def _iso_str(self, iso: str) -> str:
		return datetime.fromisoformat(iso).strftime("%m/%d %H:%M")

	def _is_now_between_isos(self, start: str, end: str) -> bool:
		return datetime.fromisoformat(start) < datetime.utcnow().replace(tzinfo=timezone.utc) < datetime.fromisoformat(end)