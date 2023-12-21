from datetime import datetime, timezone
from maubot import Plugin, MessageEvent
from maubot.handlers import command

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

class Splatoon3Bot(Plugin):
	@command.new(help="Shows you the current rotation.")
	async def splatoon3(self, evt: MessageEvent) -> None:
		resp = await self.http.get("https://splatoon3.ink/data/schedules.json")
		if not resp.ok:
			await evt.reply("Splatoon3.ink is currently down. Unable to fetch schedule data.")
			return
		data = dotdict(await resp.json()).data
		description = "**Current rotation:**"
		if data.regularSchedules.nodes[0].regularMatchSetting:
			setting = data.regularSchedules.nodes[0].regularMatchSetting
			description += "  \nTurf War: " + ", ".join(map(lambda x: x.name, setting.vsStages))
		if data.bankaraSchedules.nodes[0].bankaraMatchSettings:
			setting = data.bankaraSchedules.nodes[0].bankaraMatchSettings[0]
			description += "  \n" + setting.vsRule.name + " (Series): " + ", ".join(map(lambda x: x.name, setting.vsStages))
			setting = data.bankaraSchedules.nodes[0].bankaraMatchSettings[1]
			description += "  \n" + setting.vsRule.name + " (Open): " + ", ".join(map(lambda x: x.name, setting.vsStages))
		if data.xSchedules.nodes[0].xMatchSetting:
			setting = data.xSchedules.nodes[0].xMatchSetting
			mode = data.xSchedules.nodes[0].xMatchSetting.vsRule.name
			description += "  \n" + setting.vsRule.name + " (X): " + ", ".join(map(lambda x: x.name, setting.vsStages))
		if data.currentFest:
			# todo when splatfest happens
			pass
		if data.festSchedules.nodes[0].festMatchSettings:
			setting = data.festSchedules.nodes[0].festMatchSettings[0]
			description += "  \nSplatfest (Open): " + ", ".join(map(lambda x: x.name, setting.vsStages))
			setting = data.festSchedules.nodes[0].festMatchSettings[1]
			description += "  \nSplatfest (Pro): " + ", ".join(map(lambda x: x.name, setting.vsStages))
		
		coopSchedule = data.coopGroupingSchedule
		if len(coopSchedule.regularSchedules.nodes) > 0:
			setting = coopSchedule.regularSchedules.nodes[0].setting
			description += "\n\n**Salmon Run:**  \n" + setting.coopStage.name + " - " + setting.boss.name
			for weapon in setting.weapons:
				description += "\n- " + weapon.name
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
			description += "will happen on " + datetime.fromisoformat(nextChallengeTime.startTime).strftime("%Y-%m-%d %H:%M:%S") + " (UTC+00:00)"
		description += "  \n" + data.eventSchedules.nodes[0].leagueMatchSetting.leagueMatchEvent.desc

		await evt.reply(description)


