from util.storage import save_image_blobs, save_image_binary_blobs
import asyncio
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

temp_img_output_path = "D:/gh-repo/lego-agent/api/temp/obimg_in_20250604191355297171.jpg"

async def main2():
    with open(temp_img_output_path, mode="rb") as data:
        # async for result in save_image_binary_blobs([data]):
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url='https://mamimezf5xgqovhubstorage.blob.core.windows.net/', credential=credential
        )
        container_client = blob_service_client.get_container_client(container='sustineo')
        container_client.upload_blob(name="sample-blob.txt", data=data, overwrite=True)



async def main():
    with open(temp_img_output_path, mode="rb") as data:
        async for result in save_image_binary_blobs([data]):
            print(result)

asyncio.run(main())