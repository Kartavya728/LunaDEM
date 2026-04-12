import os
import requests
import json

# ==============================
# CONFIG
# ==============================
BASE_URL = "https://g6goyz4w56.execute-api.us-west-2.amazonaws.com/prod/collections/kaguya_terrain_camera_monoscopic_uncontrolled_observations/items/"
BASE_DIR = "dataset"

ITEM_IDS = [
    "TC1S2B0_01_07496N077E3020",
    "TC1S2B0_01_07496N087E3020",
    "TC1S2B0_01_07496N101E3020",
    "TC1S2B0_01_07496N115E3020",
    "TC1S2B0_01_07496N128E3020",
    "TC1S2B0_01_07496N142E3020",
    "TC1S2B0_01_07496N156E3020",
    "TC1S2B0_01_07496N169E3020",
    "TC1S2B0_01_07496N183E3021",
    "TC1S2B0_01_07495N079E3030",
    "TC1S2B0_01_07495N088E3030",
    "TC1S2B0_01_07495N102E3030",
    "TC1S2B0_01_07495N116E3030",
    "TC1S2B0_01_07495N130E3030",
    "TC1S2B0_01_07495N143E3030",
    "TC1S2B0_01_07495N157E3031",
    "TC1S2B0_01_07495N171E3031",
    "TC1S2B0_01_07495N184E3031"
]

# ==============================
# DOWNLOAD FUNCTION
# ==============================
def download_file(url, path):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"✅ Saved: {path}")
    except Exception as e:
        print(f"❌ Failed: {url} | {e}")

# ==============================
# MAIN LOOP
# ==============================
for item_id in ITEM_IDS:
    print(f"\n📦 Processing {item_id}")

    url = BASE_URL + item_id
    response = requests.get(url)
    data = response.json()

    # Folder structure
    item_dir = os.path.join(BASE_DIR, item_id)
    folders = {
        "image": os.path.join(item_dir, "image"),
        "preview": os.path.join(item_dir, "preview"),
        "metadata": os.path.join(item_dir, "metadata"),
        "stac": os.path.join(item_dir, "stac"),
    }

    for f in folders.values():
        os.makedirs(f, exist_ok=True)

    # Save STAC JSON
    with open(os.path.join(folders["stac"], "item.json"), "w") as f:
        json.dump(data, f, indent=4)

    assets = data["assets"]

    for key, asset in assets.items():
        url = asset["href"]

        if key == "image":
            download_file(url, os.path.join(folders["image"], "image.tif"))

        elif key == "thumbnail":
            download_file(url, os.path.join(folders["preview"], "thumbnail.jpg"))

        elif key == "caminfo_pvl":
            download_file(url, os.path.join(folders["metadata"], "caminfo.pvl"))

        elif key == "usgscsm_isd":
            download_file(url, os.path.join(folders["metadata"], "camera.json"))

        elif key == "pds_label":
            download_file(url, os.path.join(folders["metadata"], "pds.lbl"))

        elif key == "isis_label":
            download_file(url, os.path.join(folders["metadata"], "isis.lbl"))

        elif key == "provenance":
            download_file(url, os.path.join(folders["metadata"], "provenance.txt"))

print("\n🚀 Dataset ready!")