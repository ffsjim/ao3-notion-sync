import os
import requests
from notion_client import Client
from ao3_api import AO3

# -----------------------------
# ENV VARIABLES (GitHub Secrets)
# -----------------------------
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
AO3_USERNAME = os.environ["AO3_USERNAME"]

notion = Client(auth=NOTION_TOKEN)
ao3 = AO3()

# -----------------------------
# FETCH AO3 WORKS
# -----------------------------
def fetch_ao3_works(username):
    user = ao3.get_user(username)
    return user.works

# -----------------------------
# FIND NOTION PAGE BY AO3 URL
# -----------------------------
def find_notion_page(ao3_url):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "AO3 URL",
            "url": {"equals": ao3_url}
        }
    )

    results = response.get("results")
    return results[0]["id"] if results else None

# -----------------------------
# UPDATE NOTION PAGE
# -----------------------------
def update_notion_page(page_id, work):
    notion.pages.update(
        page_id=page_id,
        properties={
            "Title": {
                "title": [{"text": {"content": work.title}}]
            },
            "Hits": {"number": work.hits},
            "Kudos": {"number": work.kudos},
            "Comments": {"number": work.comments},
            "Bookmarks": {"number": work.bookmarks},
        }
    )

# -----------------------------
# SYNC PROCESS
# -----------------------------
def sync():
    print("Starting AO3 → Notion sync...")

    works = fetch_ao3_works(AO3_USERNAME)

    for work in works:
        page_id = find_notion_page(work.url)

        if not page_id:
            print(f"Skipping (not in Notion): {work.title}")
            continue

        update_notion_page(page_id, work)
        print(f"Updated: {work.title}")

    print("Sync complete.")

# -----------------------------
# ENTRY POINT (used by GitHub Actions)
# -----------------------------
if __name__ == "__main__":
    sync()
