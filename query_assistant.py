#!/usr/bin/env python
"""
Script to query the OpenAI Assistant about aviation regulations.
This script will:
1. Create a thread
2. Send a query
3. Get the response with citations
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def main():
    """Query the assistant about aviation regulations."""
    print("Initializing OpenAI client...")
    client = OpenAI()
    
    # Get assistant ID from environment or prompt
    assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    if not assistant_id:
        assistant_id = input("Enter the Assistant ID: ")
    
    # Create a thread
    print("\nCreating thread...")
    thread = client.beta.threads.create()
    
    while True:
        # Get query from user
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        # Add message to thread
        print("\nSending query to assistant...")
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Create and run
        print("Getting response...")
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Get messages
        messages = list(client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id
        ))
        
        # Print response with citations
        if messages:
            message_content = messages[0].content[0].text
            annotations = message_content.annotations
            citations = []
            
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(
                    annotation.text, f"[{index}]"
                )
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}")
            
            print("\nResponse:")
            print("-" * 50)
            print(message_content.value)
            if citations:
                print("\nCitations:")
                print("\n".join(citations))
            print("-" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Query session completed successfully!")
    else:
        print("\n❌ Query session failed!") 