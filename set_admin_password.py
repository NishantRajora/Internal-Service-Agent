from auth_utils import hash_password
from database import set_setting

if __name__ == "__main__":
    import getpass
    print("--- Veridian Corp Admin Password Setup ---")
    password = getpass.getpass("Enter new admin password: ")
    confirm_password = getpass.getpass("Confirm admin password: ")

    if password == confirm_password:
        hashed = hash_password(password)
        set_setting("admin_password", hashed)
        print("\n✅ Admin password set successfully and stored as a secure hash!")
    else:
        print("\n❌ Passwords do not match. Please try again.")
