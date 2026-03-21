import asyncio
from app.services.intent_parser_service import IntentParserService

async def main():
    service = IntentParserService()
    res = await service.parse_user_input("我想去北京玩三天")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
