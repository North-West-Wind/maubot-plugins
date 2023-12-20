from maubot import Plugin, MessageEvent
from maubot.handlers import command
import random

class ColorBot(Plugin):
	@command.new(require_subcommand=True)
	async def color(self, evt: MessageEvent) -> None:
		pass

	@color.subcommand("random", help="Returns a random color.", aliases=("r"))
	async def random(self, evt: MessageEvent) -> None:
		r = random.randint(0, 255)
		g = random.randint(0, 255)
		b = random.randint(0, 255)
		rgb = [r, g, b]
		hexColor = ''.join(list(map(lambda x: (hex(x).split('x')[-1]).zfill(2).upper(), rgb)))
		await evt.reply("Here's a random color: #" + hexColor + "\nhttps://www.northwestw.in/color/" + hexColor, markdown=False)

	@color.subcommand("show", help="Preview the given color.", aliases=("s"))
	@command.argument("hexColor", required=True, matches="[\da-fA-F]{6}", pass_raw=True)
	async def show(self, evt: MessageEvent, hexColor: str) -> None:
		await evt.reply("Here's your color: #" + hexColor + "\nhttps://www.northwestw.in/color/" + hexColor, markdown=False)
