import os
import base64
import asyncio

import httpx


def writeFile(path: str, content: str):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def readFile(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


async def get_content(url, headers):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        return response.json()


async def getManifestOnline() -> dict:
    url = "https://www.bungie.net/Platform/Destiny2/Manifest/"
    headers = {"X-API-KEY": "{}".format(os.environ.get("API_KEY"))}
    data = await get_content(url, headers)
    if data.get("ErrorCode") == 1 and data.get("Message") == "Ok":
        return data["Response"]
    else:
        raise


async def startGenerateManifest(current: str) -> None:
    buildMessage = f"New manifest build - {current}"
    url = "https://api.github.com/repos/Destiny2Bot/py-d2-additional-info/dispatches"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Basic "
        + base64.b64encode(os.environ.get("PAT", "").encode()).decode(),
        "User-Agent": "d2-additional-info",
    }
    body = {
        "event_type": "new-manifest-detected",
        "client_payload": {
            "message": buildMessage,
            "branch": "master",
            "config": {"env": {"MANIFEST_VERSION": current}},
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, json=body)
    if response.status_code != 204:
        print(response.text)
        raise


async def main():
    latest = readFile("./latest.json")
    manifestMetadata = await getManifestOnline()
    current = manifestMetadata["version"]
    newREADME = "# py-d2-manifest-bot\ngithub action for checking for new d2 manifest\n\n# Current Manifest: {current}"
    print(f"Latest: {latest}")
    print(f"Current: {current}")
    if latest == current:
        return
    print("New manifest detected")
    writeFile("latest.json", current)
    writeFile("README.md", newREADME.format(current=current))
    await startGenerateManifest(current)


if __name__ == "__main__":
    asyncio.run(main())
