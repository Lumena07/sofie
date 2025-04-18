#!/usr/bin/env python
"""
Script to set up the OpenAI Assistant with File Search for aviation regulations.
This script will:
1. Create a vector store for the regulations
2. Upload all documents from Google Drive
3. Create an assistant with file search capabilities
"""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from src.drive_integration import DriveIntegration

# Load environment variables
load_dotenv()

def main():
    """Set up the OpenAI Assistant with File Search."""
    print("Initializing OpenAI client...")
    client = OpenAI()
    
    print("\nCreating vector store for aviation regulations...")
    vector_store = client.vector_stores.create(
        name="Tanzanian Aviation Regulations",
        expires_after={
            "anchor": "last_active_at",
            "days": 30  # Keep for 30 days after last use
        }
    )
    
    print("\nGetting documents from Google Drive...")
    drive = DriveIntegration()
    documents = drive.list_files()
    
    print(f"\nFound {len(documents)} documents. Uploading to vector store...")
    
    # Upload files in batches of 10
    batch_size = 10
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} of {(len(documents) + batch_size - 1)//batch_size}...")
        
        file_streams = []
        for doc in batch:
            try:
                content, mime_type = drive.download_file(doc['id'])
                if content and mime_type:
                    # Create a unique temporary file name
                    temp_path = f"temp_{doc['id']}_{int(time.time())}.pdf"
                    
                    # Ensure the file doesn't exist
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    # Write content with proper file handling
                    with open(temp_path, 'wb') as f:
                        f.write(content)
                        f.flush()
                        os.fsync(f.fileno())
                    
                    # Small delay to ensure file is written
                    time.sleep(0.5)
                    
                    # Upload to OpenAI with proper file handling
                    with open(temp_path, "rb") as f:
                        file = client.files.create(
                            file=f,
                            purpose="assistants"
                        )
                        file_streams.append(file.id)
                    
                    # Small delay before cleanup
                    time.sleep(0.5)
                    
                    # Clean up
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    print(f"✅ Uploaded: {doc['name']}")
                else:
                    print(f"❌ Failed to download: {doc['name']}")
            except Exception as e:
                print(f"❌ Error processing {doc['name']}: {str(e)}")
                # Try to clean up if file exists
                if os.path.exists(temp_path):
                    try:
                        time.sleep(1)  # Wait a bit longer if there was an error
                        os.remove(temp_path)
                    except:
                        pass
        
        if file_streams:
            # Add files to vector store
            batch = client.vector_stores.file_batches.create_and_poll(
                vector_store_id=vector_store.id,
                file_ids=file_streams
            )
            print(f"✅ Added batch to vector store. Status: {batch.status}")
    
    print("\nCreating assistant...")
    assistant = client.beta.assistants.create(
        name="Tanzanian Aviation Regulations Assistant",
        instructions="You are an expert in Tanzanian aviation regulations. Use the provided documents to answer questions accurately and cite your sources.",
        model="gpt-4-turbo-preview",
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )
    
    print("\nSetup complete!")
    print(f"Assistant ID: {assistant.id}")
    print(f"Vector Store ID: {vector_store.id}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Assistant setup completed successfully!")
    else:
        print("\n❌ Assistant setup failed!") 