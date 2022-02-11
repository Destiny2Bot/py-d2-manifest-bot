import os
import asyncio

import httpx


async def get_content(url, headers):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        return response.json()


async def getManifestOnline() -> dict:
    """
    :说明: `getManifestOnline`
    > 在线获取manifest信息

    :返回:
        - `dict`: Bungieapi返回值
    """
    url = "https://www.bungie.net/Platform/Destiny2/Manifest/"
    headers = {"X-API-KEY": "{}".format(os.environ.get("API_KEY"))}
    data = await get_content(url, headers)
    if data.get("ErrorCode") == 1 and data.get("Message") == "Ok":
        return data["Response"]
    else:
        raise


async def main():
    manifest = await getManifestOnline()
    print("Manifest version: ", manifest["version"])


if __name__ == "__main__":
    asyncio.run(main())
