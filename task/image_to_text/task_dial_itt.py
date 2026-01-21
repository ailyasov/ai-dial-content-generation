import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._models.message import Message
from task._models.role import Role
from task._utils.bucket_client import DialBucketClient
from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT, DIAL_URL
from task._utils.model_client import DialModelClient


async def _put_image() -> Attachment:
    file_name = "dialx-banner.png"
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = "image/png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    async with DialBucketClient(
        api_key=API_KEY,
        base_url=DIAL_URL,
    ) as dial_bucket_client:
        response_json = await dial_bucket_client.put_file(
            name=file_name, mime_type=mime_type_png, content=BytesIO(image_bytes)
        )
        print(response_json)
        return Attachment(title=file_name, url=response_json["url"], type=mime_type_png)


def start() -> None:
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="anthropic.claude-haiku-4-5-20251001-v1:0",
        api_key=API_KEY,
    )

    attachment = asyncio.run(_put_image())

    messages = Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment]),
    )

    response = client.get_completion(messages=[messages], custom_fields={})
    print(response)


start()
