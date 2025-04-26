import firebase_admin
from firebase_admin import credentials, auth

# === 1. Initialize Firebase Admin SDK ===
cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# === 2. Delete all Authentication users ===
def delete_all_auth_users():
    try:
        page = auth.list_users()
        total_deleted = 0
        while page:
            for user in page.users:
                auth.delete_user(user.uid)
                print(f"✅ Deleted user: {user.email}")
                total_deleted += 1
            page = page.get_next_page()
        print(f"🎯 Finished: {total_deleted} users deleted from Authentication.")
    except Exception as e:
        print(f"❌ Error while deleting users: {e}")

# === 3. Main execution ===
if __name__ == "__main__":
   
    delete_all_auth_users()

