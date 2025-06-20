import easyocr
import asyncio

reader = easyocr.Reader(['en', 'ru'])
keywords = ["members", "subscribers"]


async def async_ocr(filepath):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, reader.readtext, filepath)
    return result

async def mem(result):
    for item in result:
        text = item[1]
        if "members" in text.lower():
            members_text = text
            members_text = members_text.replace("members", "")
            answer = int(members_text.replace(",", "").replace(" ", ""))
            break
        elif "subscribers" in text.lower():
            members_text = text
            members_text = members_text.replace("subscribers", "")
            answer = int(members_text.replace(",", "").replace(" ", ""))
            break
        elif "подписчиков" in text.lower():
            members_text = text
            members_text = members_text.replace("подписчиков", "")
            answer = int(members_text.replace(",", "").replace(" ", ""))
            break
        elif "участников" in text.lower():
            members_text = text
            members_text = members_text.replace("участников", "")
            answer = int(members_text.replace(",", "").replace(" ", ""))
            break
    return answer



async def main(m):
    result = await async_ocr(m)
    a = await mem(result)
    return a
