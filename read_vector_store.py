import os
import pickle
import glob

def read_vector_store():
    """Read and display contents of the vector store."""
    print("Searching for vector store file...")
    
    # Check all directories recursively for vector_store.pkl
    found_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'vector_store.pkl':
                path = os.path.join(root, file)
                found_files.append(path)
                print(f"Found vector store at: {path}")
    
    if not found_files:
        print("\nNo vector_store.pkl files found.")
        
        # List all .pkl files as potential candidates
        print("\nSearching for any .pkl files...")
        pkl_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pkl'):
                    path = os.path.join(root, file)
                    pkl_files.append(path)
                    print(f"Found .pkl file: {path}")
        
        if not pkl_files:
            print("No .pkl files found at all.")
        return False
    
    # Try to read each found vector store
    for path in found_files:
        print(f"\nAttempting to read {path}...")
        try:
            with open(path, 'rb') as f:
                vector_store = pickle.load(f)
            
            print("\nSuccessfully loaded vector store!")
            print("\nKnowledge Base Contents:")
            print("="*50)
            
            if not vector_store:
                print("Vector store is empty!")
                continue
            
            for doc_id, doc_data in vector_store.items():
                print(f"\nDocument ID: {doc_id}")
                print(f"Document Name: {doc_data.get('name', 'No name available')}")
                print("\nContent Preview:")
                print("-"*30)
                content = doc_data.get('content', 'No content available')
                print(content[:500] + "..." if len(content) > 500 else content)
                print("="*50)
            
            return True
        except Exception as e:
            print(f"Error reading vector store at {path}: {str(e)}")
    
    print("\nCould not successfully read any vector store files.")
    return False

if __name__ == "__main__":
    read_vector_store() 