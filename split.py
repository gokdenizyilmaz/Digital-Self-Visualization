import os
import re
import json

def normalize_filename(filename):
    name_part = os.path.splitext(filename)[0]
    match = re.match(r'(.+?)_(\d{2}_\d{2}_\d{4}_\d{2}_\d{2}_\d{2})', name_part)
    if match:
        title_raw = match.group(1)
        date_str = match.group(2)
        title = title_raw.replace("_", " ").strip()
        return title, date_str
    return None, None

def get_month_from_folder(folder_name):
    month_lookup = {
        "01": "January", "02": "February", "03": "March",
        "04": "April",   "05": "May",      "06": "June",
        "07": "July",    "08": "August",   "09": "September",
        "10": "October", "11": "November", "12": "December"
    }
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})', folder_name, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    # fallback if folder is just "2024" etc.
    match_year = re.search(r'(2023|2024|2025)', folder_name)
    if match_year:
        return "Unknown", match_year.group(1)
    return None, None

def parse_txt_file(filepath):
    messages = []
    with open(filepath, "r", encoding="utf-8") as f:
        current_role = None
        buffer = []
        for line in f:
            line = line.strip()
            if line in ["user", "ChatGPT"]:
                if current_role and buffer:
                    messages.append({"role": current_role, "content": "\n".join(buffer).strip()})
                    buffer = []
                current_role = "user" if line == "user" else "ChatGPT"
            else:
                buffer.append(line)
        if current_role and buffer:
            messages.append({"role": current_role, "content": "\n".join(buffer).strip()})
    return messages

def traverse_and_parse(root_dir="."):
    results = []
    for folder_name in os.listdir(root_dir):
        if not any(year in folder_name for year in ["2023", "2024", "2025"]):
            continue
        folder_path = os.path.join(root_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        month, year = get_month_from_folder(folder_name)
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                filepath = os.path.join(folder_path, filename)
                title, date_str = normalize_filename(filename)
                if not title or not date_str:
                    continue
                messages = parse_txt_file(filepath)
                results.append({
                    "year": year,
                    "month": month,
                    "title": title,
                    "date": date_str,
                    "messages": messages
                })
    return results

if __name__ == "__main__":
    parsed_data = traverse_and_parse()
    with open("parsed_conversations.json", "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    print("✅ JSON dosyası oluşturuldu: parsed_conversations.json")
