import base64
import os
import contextlib
from typing import AsyncGenerator
import uuid
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from dotenv import load_dotenv

load_dotenv()

SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")
SUSTINEO_CONTAINER = "sustineo"

@contextlib.asynccontextmanager
async def get_storage_client(container: str):
    # Create credential and blob service client
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=SUSTINEO_STORAGE, credential=credential
    )
    try:
        # Create the container if it doesn't exist
        container_client = blob_service_client.get_container_client(container)

        # remove the comment below if you want to ensure 
        # the container exists. commenting to avoid unnecessary 
        # creation
        if not await container_client.exists():
           await container_client.create_container()

        yield container_client
    finally:
        await credential.close()
        await blob_service_client.close()



async def save_image_blobs(images: list[str]) -> AsyncGenerator[str, None]:
    async with get_storage_client(SUSTINEO_CONTAINER) as container_client:
        for image in images:
            image_bytes = base64.b64decode(image)
            blob_name = f"images/{str(uuid.uuid4())}.png"
            await container_client.upload_blob(
                name=blob_name, data=image_bytes, overwrite=True
            )
            yield blob_name


async def save_image_binary_blobs(image: bytes) -> AsyncGenerator[str, None]:
    # print(SUSTINEO_STORAGE)
    # print(SUSTINEO_CONTAINER)
    async with get_storage_client(SUSTINEO_CONTAINER) as container_client:
        blob_name = f"images/{str(uuid.uuid4())}.jpg"
        await container_client.upload_blob(
            name=blob_name, data=image, overwrite=True
        )
        return blob_name
