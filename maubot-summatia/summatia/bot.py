from maubot import MessageEvent, Plugin
from maubot.handlers import command
from typing import Tuple

class SummatiaPlugin(Plugin):
	@command.passive("summatia",case_insensitive=True)
	async def summatia_mentioned(self, evt: MessageEvent, matches: Tuple[str]) -> None:
		if any(map(lambda x: "SUMMATIA" in x, matches)):
			await evt.react("‼️")
		else:
			await evt.react("❗")