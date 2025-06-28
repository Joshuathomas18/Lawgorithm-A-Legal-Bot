"""
Main LangGraph Petition Workflow
===============================

Orchestrates the complete petition generation process using LangGraph.
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from langgraph_petition_system.state_management import PetitionState, StateManager
from langgraph_petition_system.rag_systems.dual_rag_interface import DualRAGInterface
from langgraph_petition_system.prompts.xml_prompt_templates import XMLPromptBuilder, PromptValidator
from langgraph_petition_system.config import Jurisdiction, PetitionType, LLM_CONFIG

logger = logging.getLogger(__name__)

class LangGraphPetitionWorkflow:
    """Main workflow for petition generation using LangGraph"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.dual_rag = DualRAGInterface()
        self.prompt_builder = XMLPromptBuilder()
        self.prompt_validator = PromptValidator()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        # Create state graph
        workflow = StateGraph(PetitionState)
        
        # Add nodes
        workflow.add_node("input_processor", self._input_processor_node)
        workflow.add_node("dual_rag_retriever", self._dual_rag_retriever_node)
        workflow.add_node("prompt_builder", self._prompt_builder_node)
        workflow.add_node("llm_generator", self._llm_generator_node)
        workflow.add_node("output_validator", self._output_validator_node)
        workflow.add_node("feedback_handler", self._feedback_handler_node)
        workflow.add_node("output_formatter", self._output_formatter_node)
        
        # Define the flow
        workflow.set_entry_point("input_processor")
        
        # Main flow
        workflow.add_edge("input_processor", "dual_rag_retriever")
        workflow.add_edge("dual_rag_retriever", "prompt_builder")
        workflow.add_edge("prompt_builder", "llm_generator")
        workflow.add_edge("llm_generator", "output_validator")
        
        # Conditional flow based on validation
        workflow.add_conditional_edges(
            "output_validator",
            self._should_continue,
            {
                "continue": "output_formatter",
                "feedback": "feedback_handler",
                "error": END
            }
        )
        
        # Feedback loop
        workflow.add_edge("feedback_handler", "prompt_builder")
        
        # Final output
        workflow.add_edge("output_formatter", END)
        
        # Add memory for state persistence
        memory = MemorySaver()
        workflow.set_checkpointer(memory)
        
        return workflow.compile()
    
    def _input_processor_node(self, state: PetitionState) -> PetitionState:
        """Process and validate input"""
        try:
            logger.info(f"Processing input for session: {state['session_id']}")
            
            # Validate input
            if not self.state_manager.validate_state(state):
                return self.state_manager.add_error(state, "Invalid input state")
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "input_processing", "success", 
                f"Processed input for {state['jurisdiction'].value} - {state['petition_type'].value}"
            )
            
            logger.info("Input processing completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in input processing: {e}")
            return self.state_manager.add_error(state, f"Input processing error: {str(e)}")
    
    def _dual_rag_retriever_node(self, state: PetitionState) -> PetitionState:
        """Retrieve context from dual RAG systems"""
        try:
            logger.info(f"Retrieving dual RAG context for session: {state['session_id']}")
            
            # Create query from user input and case details
            query = self._create_rag_query(state)
            
            # Retrieve from dual RAG
            rag_results = self.dual_rag.retrieve_dual_context(
                query, state['jurisdiction'], state['petition_type'], top_k=5
            )
            
            # Update state with RAG results
            updates = {
                'structure_chunks': rag_results.get('structure_chunks', []),
                'content_chunks': rag_results.get('content_chunks', [])
            }
            
            state = self.state_manager.update_state(state, updates)
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "dual_rag_retrieval", "success",
                f"Retrieved {len(updates['structure_chunks'])} structure chunks and {len(updates['content_chunks'])} content chunks"
            )
            
            logger.info("Dual RAG retrieval completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in dual RAG retrieval: {e}")
            return self.state_manager.add_error(state, f"RAG retrieval error: {str(e)}")
    
    def _prompt_builder_node(self, state: PetitionState) -> PetitionState:
        """Build XML prompt from RAG results"""
        try:
            logger.info(f"Building XML prompt for session: {state['session_id']}")
            
            # Build XML prompt
            xml_prompt = self.prompt_builder.build_prompt(state)
            
            # Validate prompt
            if not self.prompt_validator.validate_xml_structure(xml_prompt):
                missing_elements = self.prompt_validator.check_required_elements(xml_prompt)
                return self.state_manager.add_error(
                    state, f"Invalid XML prompt structure. Missing elements: {missing_elements}"
                )
            
            # Update state
            state = self.state_manager.update_state(state, {'final_prompt': xml_prompt})
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "prompt_building", "success",
                f"Built XML prompt with {len(xml_prompt)} characters"
            )
            
            logger.info("XML prompt building completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in prompt building: {e}")
            return self.state_manager.add_error(state, f"Prompt building error: {str(e)}")
    
    def _llm_generator_node(self, state: PetitionState) -> PetitionState:
        """Generate petition using LLM"""
        try:
            logger.info(f"Generating petition with LLM for session: {state['session_id']}")
            
            # Get the XML prompt
            xml_prompt = state.get('final_prompt', '')
            if not xml_prompt:
                return self.state_manager.add_error(state, "No XML prompt available")
            
            # Generate using LLM (integrate with existing Ollama service)
            llm_output = self._call_llm(xml_prompt)
            
            if not llm_output:
                return self.state_manager.add_error(state, "LLM generation failed")
            
            # Update state
            state = self.state_manager.update_state(state, {'llm_output': llm_output})
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "llm_generation", "success",
                f"Generated petition with {len(llm_output)} characters"
            )
            
            logger.info("LLM generation completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            return self.state_manager.add_error(state, f"LLM generation error: {str(e)}")
    
    def _output_validator_node(self, state: PetitionState) -> PetitionState:
        """Validate the generated output"""
        try:
            logger.info(f"Validating output for session: {state['session_id']}")
            
            llm_output = state.get('llm_output', '')
            if not llm_output:
                return self.state_manager.add_error(state, "No LLM output to validate")
            
            # Validate the output
            validation_result = self._validate_petition_output(llm_output, state)
            
            if validation_result['is_valid']:
                # Update state with validated output
                state = self.state_manager.update_state(state, {
                    'validated_output': llm_output
                })
                
                # Add processing step
                state = self.state_manager.add_processing_step(
                    state, "output_validation", "success",
                    validation_result['message']
                )
                
                logger.info("Output validation completed successfully")
                return state
            else:
                # Add error and continue to feedback
                state = self.state_manager.add_error(state, validation_result['message'])
                
                # Add processing step
                state = self.state_manager.add_processing_step(
                    state, "output_validation", "error",
                    validation_result['message']
                )
                
                logger.warning(f"Output validation failed: {validation_result['message']}")
                return state
                
        except Exception as e:
            logger.error(f"Error in output validation: {e}")
            return self.state_manager.add_error(state, f"Validation error: {str(e)}")
    
    def _feedback_handler_node(self, state: PetitionState) -> PetitionState:
        """Handle feedback and refine the process"""
        try:
            logger.info(f"Handling feedback for session: {state['session_id']}")
            
            # Get the error message
            error_message = state.get('errors', '')
            
            # Create refined prompt based on error
            refined_prompt = self._create_refined_prompt(state, error_message)
            
            # Update state with refined prompt
            state = self.state_manager.update_state(state, {
                'final_prompt': refined_prompt,
                'errors': None  # Clear the error
            })
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "feedback_handling", "success",
                f"Refined prompt based on error: {error_message[:100]}..."
            )
            
            logger.info("Feedback handling completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in feedback handling: {e}")
            return self.state_manager.add_error(state, f"Feedback handling error: {str(e)}")
    
    def _output_formatter_node(self, state: PetitionState) -> PetitionState:
        """Format the final output"""
        try:
            logger.info(f"Formatting final output for session: {state['session_id']}")
            
            validated_output = state.get('validated_output', '')
            if not validated_output:
                return self.state_manager.add_error(state, "No validated output to format")
            
            # Format the output (could include additional formatting here)
            formatted_output = self._format_final_output(validated_output, state)
            
            # Update state
            state = self.state_manager.update_state(state, {
                'validated_output': formatted_output
            })
            
            # Add processing step
            state = self.state_manager.add_processing_step(
                state, "output_formatting", "success",
                "Final output formatted successfully"
            )
            
            logger.info("Output formatting completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in output formatting: {e}")
            return self.state_manager.add_error(state, f"Output formatting error: {str(e)}")
    
    def _should_continue(self, state: PetitionState) -> str:
        """Determine the next step based on validation result"""
        if state.get('errors'):
            return "feedback"
        elif state.get('validated_output'):
            return "continue"
        else:
            return "error"
    
    def _create_rag_query(self, state: PetitionState) -> str:
        """Create query for RAG retrieval"""
        case_details = state.get('case_details', {})
        
        query_parts = [
            state.get('user_input', ''),
            case_details.get('facts', ''),
            case_details.get('legal_grounds', ''),
            case_details.get('relief', '')
        ]
        
        return " ".join([part for part in query_parts if part])
    
    def _call_llm(self, xml_prompt: str) -> str:
        """Call the LLM with the XML prompt"""
        try:
            # This would integrate with your existing Ollama service
            # For now, return a placeholder
            return f"Generated petition based on XML prompt: {xml_prompt[:100]}..."
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return ""
    
    def _validate_petition_output(self, output: str, state: PetitionState) -> Dict[str, Any]:
        """Validate the generated petition output"""
        try:
            # Basic validation checks
            required_sections = ['FACTS', 'GROUNDS', 'RELIEF']
            missing_sections = []
            
            for section in required_sections:
                if section not in output.upper():
                    missing_sections.append(section)
            
            if missing_sections:
                return {
                    'is_valid': False,
                    'message': f"Missing required sections: {', '.join(missing_sections)}"
                }
            
            # Check for minimum length
            if len(output) < 500:
                return {
                    'is_valid': False,
                    'message': "Generated petition is too short (less than 500 characters)"
                }
            
            return {
                'is_valid': True,
                'message': "Petition validation passed"
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'message': f"Validation error: {str(e)}"
            }
    
    def _create_refined_prompt(self, state: PetitionState, error_message: str) -> str:
        """Create a refined prompt based on error feedback"""
        original_prompt = state.get('final_prompt', '')
        
        # Add error context to the prompt
        refined_prompt = f"{original_prompt}\n\nERROR_FEEDBACK: {error_message}\n\nPlease address the above error and regenerate the petition."
        
        return refined_prompt
    
    def _format_final_output(self, output: str, state: PetitionState) -> str:
        """Format the final output"""
        # Add metadata to the output
        metadata = f"""
Generated by LangGraph Petition System
Session ID: {state.get('session_id', 'Unknown')}
Jurisdiction: {state.get('jurisdiction', 'Unknown')}
Petition Type: {state.get('petition_type', 'Unknown')}
Generated at: {state.get('timestamp', 'Unknown')}
"""
        
        return f"{metadata}\n\n{output}"
    
    def generate_petition(self, user_input: str, jurisdiction: Jurisdiction, 
                         petition_type: PetitionType, case_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a petition using the LangGraph workflow"""
        try:
            logger.info(f"Starting petition generation workflow")
            
            # Create initial state
            initial_state = self.state_manager.create_initial_state(
                user_input, jurisdiction, petition_type, case_details
            )
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Get result
            result = {
                'success': not bool(final_state.get('errors')),
                'petition_text': final_state.get('validated_output', ''),
                'session_id': final_state.get('session_id', ''),
                'processing_steps': final_state.get('processing_steps', []),
                'errors': final_state.get('errors'),
                'metadata': self.state_manager.get_state_summary(final_state)
            }
            
            logger.info(f"Petition generation completed: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in petition generation workflow: {e}")
            return {
                'success': False,
                'petition_text': '',
                'session_id': '',
                'processing_steps': [],
                'errors': str(e),
                'metadata': {}
            }

def main():
    """Test the LangGraph workflow"""
    # Create workflow
    workflow = LangGraphPetitionWorkflow()
    
    # Test case details
    case_details = {
        'petitioner_name': 'John Doe',
        'respondent_name': 'Jane Smith',
        'incident_date': '2024-01-15',
        'filing_date': '2024-02-01',
        'case_number': 'CR123/2024',
        'facts': 'The petitioner alleges breach of contract by the respondent.',
        'evidence': 'Contract documents and correspondence.',
        'relief': 'Compensation for damages and specific performance.',
        'legal_grounds': 'Breach of contract under Indian Contract Act.'
    }
    
    # Generate petition
    result = workflow.generate_petition(
        user_input="Generate a civil petition for breach of contract",
        jurisdiction=Jurisdiction.HIGH_COURT,
        petition_type=PetitionType.CIVIL_PETITION,
        case_details=case_details
    )
    
    print(f"Generation successful: {result['success']}")
    print(f"Session ID: {result['session_id']}")
    if result['success']:
        print(f"Petition length: {len(result['petition_text'])} characters")
    else:
        print(f"Error: {result['errors']}")

if __name__ == "__main__":
    main() 