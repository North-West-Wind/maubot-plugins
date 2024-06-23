import io
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import ImageInfo, MediaMessageEventContent, MessageType
from PIL import Image
import random
from typing import TypedDict

class JitsiPlugin(Plugin):
	@command.new(help="Print the Jitsi Meet link name for this room, if enabled.", require_subcommand=False)
	async def jitsi(self, evt: MessageEvent) -> None:
		states = await self.client.get_state(evt.room_id)
		filtered = list(filter(lambda x: str(x["type"]) == "im.vector.modular.widgets" and x["content"]["type"] == "jitsi", states))
		if len(filtered) == 0:
			await evt.reply("This room doesn't have Jitsi!")
		else:
			state = filtered[0]
			await evt.reply("https://" + state["content"]["data"]["domain"] + "/" + state["content"]["data"]["conferenceId"])