# Sofie - Aviation Regulations Assistant

Sofie is an AI-powered assistant that helps users navigate and understand Tanzanian aviation regulations. It uses OpenAI's GPT-4 model and integrates with Google Drive to maintain an up-to-date knowledge base of aviation documents.

## Features

- Natural language query processing for aviation regulations
- Integration with Google Drive for document management
- Real-time knowledge base updates
- Agent traces for monitoring and debugging
- Vercel deployment ready

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id
   ```

## Project Structure

- `src/agent_orchestrator.py`: Core agent logic and OpenAI integration
- `src/drive_integration.py`: Google Drive integration for document management
- `src/document_processor.py`: Document processing and knowledge base management
- `vercel_app.py`: FastAPI application entry point for Vercel deployment

## API Endpoints

- `GET /api/health`: Health check endpoint
- `POST /api/query`: Process natural language queries
- `POST /api/update-knowledge`: Update the knowledge base
- `GET /api/traces`: Retrieve agent interaction traces

## Development

To run the application locally:

```bash
uvicorn vercel_app:app --reload
```

## Deployment

The application is configured for deployment on Vercel. Simply connect your repository to Vercel and it will automatically deploy using the configuration in `vercel.json`.

## License

MIT License 