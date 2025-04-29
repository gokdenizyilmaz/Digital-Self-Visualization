import os
import json
import re  # Importing the regular expression module
from datetime import datetime

# Define the function to get conversation messages
def get_conversation_messages(conversation):
    messages = []
    current_node = conversation.get("current_node")
    mapping = conversation.get("mapping", {})
    while current_node:
        node = mapping.get(current_node, {})
        message = node.get("message") if node else None
        content = message.get("content") if message else None
        author = message.get("author", {}).get("role", "") if message else ""
        if content and content.get("content_type") == "text":
            parts = content.get("parts", [])
            if parts and len(parts) > 0 and len(parts[0]) > 0:
                if author != "system" or (message.get("metadata", {}) if message else {}).get("is_user_system_message"):
                    if author == "assistant":
                        author = "ChatGPT"
                    elif author == "system":
                        author = "Custom user info"
                    messages.append({"author": author, "text": parts[0]})
        current_node = node.get("parent") if node else None
    return messages[::-1]

# Define the function to write conversations and create pruned.json
def write_conversations_and_json(conversations_data):
    created_directories_info = []
    pruned_data = {}
    for conversation in conversations_data:
        updated = conversation.get('update_time')
        if not updated:
            continue
        
        updated_date = datetime.fromtimestamp(updated)
        directory_name = updated_date.strftime('%B_%Y')
        directory_path = os.path.join('./', directory_name)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        
        title = conversation.get('title', 'Untitled')
        sanitized_title = re.sub(r"[^a-zA-Z0-9_]", "_", title)[:120]
        file_name = f"{directory_path}/{sanitized_title}_{updated_date.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
        
        messages = get_conversation_messages(conversation)
        with open(file_name, 'w', encoding="utf-8") as file:
            for message in messages:
                file.write(f"{message['author']}\n")
                file.write(f"{message['text']}\n")
        
        if directory_name not in pruned_data:
            pruned_data[directory_name] = []
        
        pruned_data[directory_name].append({
            "title": title,
            "create_time": datetime.fromtimestamp(conversation.get('create_time')).strftime('%Y-%m-%d %H:%M:%S'),
            "update_time": updated_date.strftime('%Y-%m-%d %H:%M:%S'),
            "messages": messages
        })
        
        created_directories_info.append({
            "directory": directory_path,
            "file": file_name
        })
    
    with open('./pruned.json', 'w', encoding='utf-8') as json_file:
        json.dump(pruned_data, json_file, ensure_ascii=False, indent=4)
    
    return created_directories_info

# Load the conversations.json data and run the function to write conversations to files and create pruned.json
with open('conversations.json', 'r', encoding='utf-8') as file:
    conversations_data = json.load(file)

created_directories_info = write_conversations_and_json(conversations_data)


#https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144