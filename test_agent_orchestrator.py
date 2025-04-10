"""
Test file for the agent orchestrator.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from src.agent_orchestrator import AgentOrchestrator

class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for the AgentOrchestrator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-api-key'
        })
        self.env_patcher.start()
        
        # Create agent orchestrator instance
        self.orchestrator = AgentOrchestrator()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('openai.OpenAI')
    def test_initialize_agent(self, mock_openai):
        """Test agent initialization."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock agent creation
        mock_agent = MagicMock()
        mock_agent.id = 'test-agent-id'
        mock_client.agents.create.return_value = mock_agent
        
        # Initialize agent
        self.orchestrator.initialize_agent()
        
        # Verify agent was created
        mock_client.agents.create.assert_called_once()
        self.assertEqual(self.orchestrator.agent_id, 'test-agent-id')
    
    @patch('openai.OpenAI')
    def test_process_query_with_agent(self, mock_openai):
        """Test query processing with agent."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock thread creation
        mock_thread = MagicMock()
        mock_thread.id = 'test-thread-id'
        mock_client.threads.create.return_value = mock_thread
        
        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = 'test-run-id'
        mock_client.threads.runs.create.return_value = mock_run
        
        # Mock run status
        mock_run_status = MagicMock()
        mock_run_status.status = 'completed'
        mock_client.threads.runs.retrieve.return_value = mock_run_status
        
        # Mock messages
        mock_message = MagicMock()
        mock_message.role = 'assistant'
        mock_message.content = [MagicMock(text=MagicMock(value='Test response'))]
        mock_messages = MagicMock()
        mock_messages.data = [mock_message]
        mock_client.threads.messages.list.return_value = mock_messages
        
        # Set agent ID
        self.orchestrator.agent_id = 'test-agent-id'
        
        # Process query
        result = self.orchestrator.process_query('Test query')
        
        # Verify result
        self.assertEqual(result['answer'], 'Test response')
        self.assertEqual(result['confidence'], 0.8)
    
    @patch('src.knowledge_base.KnowledgeBase')
    def test_process_query_fallback(self, mock_knowledge_base):
        """Test query processing fallback to knowledge base."""
        # Mock knowledge base
        mock_kb = MagicMock()
        mock_knowledge_base.return_value = mock_kb
        mock_kb.query_knowledge_base.return_value = {
            'answer': 'Fallback response',
            'confidence': 0.5
        }
        
        # Set agent ID to None to trigger fallback
        self.orchestrator.agent_id = None
        
        # Process query
        result = self.orchestrator.process_query('Test query')
        
        # Verify result
        self.assertEqual(result['answer'], 'Fallback response')
        self.assertEqual(result['confidence'], 0.5)
        mock_kb.query_knowledge_base.assert_called_once_with('Test query')
    
    @patch('src.knowledge_base.KnowledgeBase')
    def test_update_knowledge_base(self, mock_knowledge_base):
        """Test knowledge base update."""
        # Mock knowledge base
        mock_kb = MagicMock()
        mock_knowledge_base.return_value = mock_kb
        mock_kb.update_knowledge_base.return_value = True
        
        # Update knowledge base
        result = self.orchestrator.update_knowledge_base()
        
        # Verify result
        self.assertTrue(result)
        mock_kb.update_knowledge_base.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_get_agent_traces(self, mock_openai):
        """Test getting agent traces."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock traces
        mock_traces = MagicMock()
        mock_traces.data = ['trace1', 'trace2']
        mock_client.agents.traces.list.return_value = mock_traces
        
        # Set agent ID
        self.orchestrator.agent_id = 'test-agent-id'
        
        # Get traces
        traces = self.orchestrator.get_agent_traces()
        
        # Verify traces
        self.assertEqual(traces, ['trace1', 'trace2'])
        mock_client.agents.traces.list.assert_called_once_with(agent_id='test-agent-id')

if __name__ == '__main__':
    unittest.main() 