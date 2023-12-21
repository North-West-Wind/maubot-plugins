import io
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import ImageInfo, MediaMessageEventContent, MessageType
from PIL import Image
import random
from typing import TypedDict

class UploadedImage(TypedDict):
	url: str
	info: ImageInfo

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
		img: UploadedImage = await self._upload_image(rgb)
		url = img["url"]
		info = img["info"]
		await evt.reply("Here's a random color: #" + hexColor)
		await evt.respond(MediaMessageEventContent(url=url, info=info, body=hexColor + ".png", msgtype=MessageType.IMAGE))

	@color.subcommand("show", help="Preview the given color.", aliases=("s"))
	@command.argument("hexColor", required=True, matches="[\da-fA-F]{6}", pass_raw=True)
	async def show(self, evt: MessageEvent, hexColor: str) -> None:
		parsedHex = int(hexColor, 16)
		b = parsedHex % 0x100
		g = (parsedHex // 0x100) % 0x100
		r = parsedHex // 0x10000
		rgb = [r, g, b]
		img: UploadedImage = await self._upload_image(rgb)
		url = img["url"]
		info = img["info"]
		await evt.reply("Here's your color: #" + hexColor)
		await evt.respond(MediaMessageEventContent(url=url, info=info, body=hexColor + ".png", msgtype=MessageType.IMAGE))

	async def _upload_image(self, rgb: list[int]) -> UploadedImage:
		hexColor = ''.join(list(map(lambda x: (hex(x).split('x')[-1]).zfill(2).upper(), rgb)))
		info = ImageInfo()
		# generate the image
		img = Image.new("RGB", (128, 32), tuple(rgb))
		imgByteArr = io.BytesIO()
		img.save(imgByteArr, format="PNG")
		imgByteArr = imgByteArr.getvalue()
		# write image info
		info.mimetype = "image/png"
		info.size = len(imgByteArr)
		info.width, info.height = img.size
		# upload color image
		url = await self.client.upload_media(imgByteArr, info.mimetype, hexColor + ".png")
		return { "url": url, "info": info }
