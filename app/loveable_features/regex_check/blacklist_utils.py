"""
Narzędzia CLI do zarządzania blacklistą: podgląd, eksport, ręczna edycja.
"""
from typing import Dict, List

from fastapi import Request

from app.loveable_features.regex_check.blacklist import UserBlacklist


async def manually_add_to_blacklist(request: Request, username: str, category: str, reason: str = "manually added"):
    blacklist = UserBlacklist(request)
    await blacklist.add_user(username, category, reason)


async def manually_remove_from_blacklist(request: Request, username: str):
    blacklist = UserBlacklist(request)
    await blacklist.remove_user(username)


async def show_blacklist(request: Request):
    blacklist = UserBlacklist(request)
    items = await blacklist.export_list()
    if not items:
        print("\n📝 Blacklista jest pusta")
        return

    print("\n" + "=" * 60)
    print("BLACKLISTA UŻYTKOWNIKÓW")
    print("=" * 60)
    stats = await blacklist.get_stats()
    print(f"\n📊 Statystyki: {len(items)} użytkowników")
    for category, count in stats.items():
        print(f"   - {category}: {count}")
    print("\n" + "=" * 60)

    categories: Dict[str, List] = {}
    for item in items:
        categories.setdefault(item["category"], []).append(item)

    for category, users in categories.items():
        print(f"\n🚫 {category.upper()}:")
        for user in users:
            print(f"   - {user['username']} (dodano: {user['added_date'][:10]})")
            if user.get("reason"):
                print(f"     └─ {user['reason'][:60]}...")


async def export_blacklist_txt(request: Request, filename: str = "blacklist_export.txt"):
    blacklist = UserBlacklist(request)
    items = await blacklist.export_list()
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item['username']}\t{item['category']}\t{item['added_date']}\n")
    print(f"✅ Blacklista wyeksportowana do {filename}")


def show_candidates(candidates: list):
    print("LISTA KANDYDATÓW:")
    print("-" * 80)
    for i, c in enumerate(candidates, 1):
        print(f"{i}. {c['username']}")
        print(f"   [{c['timestamp']}] {c['message'][:70]}...")
        print()