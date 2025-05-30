import os
import io
import base64
import json
from typing import Annotated

import aiohttp
from api.agent.decorators import agent
from api.model import AgentUpdateEvent, Content
from api.agent.storage import save_image_blobs
from api.agent.common import execute_foundry_agent, post_request


AZURE_IMAGE_ENDPOINT = os.environ.get("AZURE_IMAGE_ENDPOINT", "EMPTY").rstrip("/")
AZURE_IMAGE_API_KEY = os.environ.get("AZURE_IMAGE_API_KEY", "EMPTY")


@agent(
    name="Image Generation Agent",
    description="This agent can generate a number of images based upon a detailed description. This agent is based on the GPT-Image-1 model and is capable of generating images in a variety of styles. It can also generate images in a specific style, such as a painting or a photograph. The agent can also generate images with different levels of detail and complexity.",
)
async def gpt_image_generation(
    description: Annotated[
        str,
        "The detailed description of the image to be generated. The more detailed the description, the better the image will be. Make sure to include the style of the image, the colors, and any other details that will help the model generate a better image.",
    ],
    n: Annotated[int, "number of images to generate"],
    notify: AgentUpdateEvent,
) -> list[str]:

    await notify(
        id="image_generation",
        status="run in_progress",
        information="Starting image generation",
    )

    size: str = "1024x1024"
    quality: str = "low"
    api_version = "2025-04-01-preview"
    deployment_name = "gpt-image-1"
    endpoint = f"{AZURE_IMAGE_ENDPOINT}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"

    await notify(
        id="image_generation", status="step in_progress", information="Executing Model"
    )

    async with post_request(
        endpoint,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AZURE_IMAGE_API_KEY}",
        },
        json={
            "prompt": description,
            "size": size,
            "quality": quality,
            "output_compression": 100,
            "output_format": "png",
            "n": n,
        },
    ) as response:
        if "error" in response:
            print(response["error"])
            await notify(
                id="image_generation",
                status="step failed",
                information=response["error"],
            )
            return []

        await notify(
            id="image_generation",
            status="step in_progress",
            information="fetching images" if n > 1 else "fetching image",
        )

        # save the image to a file
        # iterate through the images and save them
        if not response["data"]:
            print("No images found in the response.")
            return []

        await notify(
            id="image_generation",
            status="step in_progress",
            information="storing images" if n > 1 else "storing image",
        )

        base64_images = [
            item["b64_json"] for item in response["data"] if item["b64_json"]
        ]

        images = []
        async for blob_name in save_image_blobs(base64_images):
            images.append(blob_name)
            await notify(
                id="image_generation",
                status="step completed",
                content=Content(
                    type="image",
                    content=[
                        {
                            "type": "image",
                            "description": description,
                            "size": size,
                            "quality": quality,
                            "image_url": blob_name,
                        }
                    ],
                ),
                output=True,
            )

        await notify(
            id="image_generation",
            status="run completed",
            information="Image generation complete",
        )

        return images


@agent(
    name="Image Editing Agent",
    description="""
    This tool can edit an image based upon a detailed description and a provided image. 
    Trigger this tool with a description of the edit to be made along with
    a kind parameter that indicates whether the image is a file upload
    or a camera capture. The image will be used as a starting point for the edit.
    The more detailed the description, the better the image will be.
    The image itself will be automatically provided as a file or a camera capture,
    so you do not need to include the image in the request. If the user is uploading a file, 
    set the kind to "FILE" - the user will explictly mention an "upload". If the user is 
    capturing an image with their camera, set the kind to "CAMERA" - the user will explicitly 
    mention a "camera capture" or say "take a picture". IMPORTANT: Do not ask the user to upload an image,
    or to take a picture, as soon as you issue the function call the UI will handle this for 
    you based on the kind parameter - it is important that you do not ask the user to upload an image or take a picture,
    as this will cause the UI to not work correctly - just provide the description and the kind parameter.
    The image will be edited based on the description provided.
    """,
)
async def gpt_image_edit(
    description: Annotated[
        str,
        "The detailed prompt of image to be edited. The more detailed the description, the better the image will be. Make sure to include the style of the image, the colors, and any other details that will help the model generate a better image.",
    ],
    image: Annotated[
        str,
        "The base64 encoded image to be used as a starting point for the generation. You do not need to include the image itself, you can add a placeholder here since the UI will handle the image upload.",
    ],
    kind: Annotated[
        str,
        'This can be either a file upload or an image that is captured with the users camera. Choose "FILE" if the image is uploaded from the users device. Choose "CAMERA" if the image should be captured with the users camera.',
    ],
    notify: AgentUpdateEvent,
) -> list[str]:
    await notify(
        id="image_edit",
        status="run in_progress",
        information="Starting image edit",
    )

    api_version = "2025-04-01-preview"
    deployment_name = "gpt-image-1"
    endpoint = f"{AZURE_IMAGE_ENDPOINT}/openai/deployments/{deployment_name}/images/edits?api-version={api_version}"

    await notify(
        id="image_edit", status="step in_progress", information="Executing Model"
    )

    size: str = "1024x1024"
    quality: str = "low"

    # send image as multipart/form-data
    if image.startswith("data:image/jpeg;base64,"):
        image = image.replace("data:image/jpeg;base64,", "")
        
    form_data = aiohttp.FormData()
    img = io.BytesIO(base64.b64decode(image))
    form_data.add_field("image", img, filename="image.jpg", content_type="image/jpeg")
    form_data.add_field("prompt", description, content_type="text/plain")
    form_data.add_field("size", size, content_type="text/plain")
    form_data.add_field("quality", quality, content_type="text/plain")

    async with post_request(
        endpoint,
        headers={
            "Authorization": f"Bearer {AZURE_IMAGE_API_KEY}",
        },
        data=form_data,
    ) as response:
        if "error" in response:
            print(json.dumps(response, indent=2))
            await notify(
                id="image_generation",
                status="step failed",
                information=response["error"],
            )
            return []

        await notify(
            id="image_edit",
            status="step in_progress",
            information="fetching image",
        )

        # save the image to a file
        # iterate through the images and save them
        if not response["data"]:
            print("No images found in the response.")
            return []

        await notify(
            id="image_edit",
            status="step in_progress",
            information="storing image",
        )

        base64_images = [
            item["b64_json"] for item in response["data"] if item["b64_json"]
        ]

        images = []
        async for blob in save_image_blobs(base64_images):
            images.append(blob)
            await notify(
                id="image_edit",
                status="step completed",
                content=Content(
                    type="image",
                    content=[
                        {
                            "type": "image",
                            "description": description,
                            "image_url": blob,
                            "kind": kind,
                        }
                    ],
                ),
                output=True,
            )

        await notify(
            id="image_edit",
            status="run completed",
            information="Image edit complete",
        )

        return images


@agent(
    name="BuildEvents - Post to LinkedIn Agent - Local",
    description="""
You are a publishing agent responsible for posting finalized and approved LinkedIn posts. 

You will receive as input:
- title (string): Title of the post.
- content (string): Body of the post or finalized draft.
- image_url (string, optional): Format should always start with https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/
- example image_url: https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/acd7fe97-8d22-48ca-a06c-d38b769a8924.png
- use the provided image_url

You will take the draft and publish the post on LinkedIn by calling the OpenAPI tool.""",
)
async def publish_linkedin_post(
    content: Annotated[str, "Body of the post or finalized draft in markdown."],
    image_url: Annotated[
        str,
        "Format should always start with https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/",
    ],
    notify: AgentUpdateEvent,
):
    instructions = f"""
Use the following `image_url`: {image_url}
Use this `image_url` exactly as it is. Do not change the image_url or the content of the post.
The post should be in markdown format.
"""
    await execute_foundry_agent(
        agent_id="asst_MbvKNQxeTr5DL1wuE8DRYR3M",
        additional_instructions=instructions,
        query=f"Can you write a LinkedIn post based on the following content?\n\n{content}",
        tools={},
        notify=notify,
    )
