"""
Zarządzanie blacklistą użytkowników (zapis/odczyt MongoDB).
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import Request

logger = logging.getLogger(__name__)

BLACKLIST_COLLECTION = "blacklist"


# Schema dokumentu w MongoDB:
# {
#   "username": str,          # unikalny klucz (używany jako _id)
#   "category": str,          # np. "admin", "spammer"
#   "added_date": str,        # ISO 8601, np. "2026-02-26T10:35:33.372459"
#   "reason": str             # opis powodu dodania
# }


class UserBlacklist:
    def __init__(self, request: Request):
        self._col = request.app.mongodb[BLACKLIST_COLLECTION]

    async def add_user(self, username: str, category: str, reason: str = "auto-detected"):
        if not await self.is_blacklisted(username):
            await self._col.insert_one({
                "_id": username,
                "username": username,
                "category": category,
                "added_date": datetime.now().isoformat(),
                "reason": reason,
            })

    async def is_blacklisted(self, username: str) -> bool:
        doc = await self._col.find_one({"_id": username}, {"_id": 1})
        return doc is not None

    async def get_category(self, username: str) -> Optional[str]:
        doc = await self._col.find_one({"_id": username}, {"category": 1})
        return doc["category"] if doc else None

    async def get_info(self, username: str) -> Optional[Dict]:
        doc = await self._col.find_one({"_id": username}, {"_id": 0})
        return doc

    async def remove_user(self, username: str):
        await self._col.delete_one({"_id": username})

    async def export_list(self) -> List[Dict]:
        cursor = self._col.find({}, {"_id": 0})
        return await cursor.to_list(length=None)

    async def get_stats(self) -> Dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        cursor = self._col.aggregate(pipeline)
        return {doc["_id"]: doc["count"] async for doc in cursor}