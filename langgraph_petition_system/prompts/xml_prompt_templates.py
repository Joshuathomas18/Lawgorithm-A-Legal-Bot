"""
XML Prompt Templates for LangGraph Petition System
"""

from typing import Dict, Any, List
from langgraph_petition_system.config import Jurisdiction, PetitionType, JURISDICTION_CONFIG, PETITION_TYPE_CONFIG

class XMLPromptBuilder:
    """Builds XML-formatted prompts for LLM petition generation"""
    
    def __init__(self):
        self.base_template = self._get_base_template()
    
    def _get_base_template(self) -> str:
        """Get the base XML template"""
        return """<petition_request>
    <query_context>
        <user_input>{user_input}</user_input>
        <jurisdiction>{jurisdiction}</jurisdiction>
        <petition_type>{petition_type}</petition_type>
        <case_details>
            <parties>{petitioner} vs {respondent}</parties>
            <incident_date>{incident_date}</incident_date>
            <filing_date>{filing_date}</filing_date>
            <case_number>{case_number}</case_number>
        </case_details>
    </query_context>
    
    <retrieved_structure>
        <document_templates>
            {structure_templates}
        </document_templates>
        <legal_phrases>
            {legal_phrases}
        </legal_phrases>
        <formatting_rules>
            {formatting_rules}
        </formatting_rules>
    </retrieved_structure>
    
    <retrieved_content>
        <relevant_cases>
            {relevant_cases}
        </relevant_cases>
        <legal_arguments>
            {legal_arguments}
        </legal_arguments>
        <precedents>
            {precedents}
        </precedents>
    </retrieved_content>
    
    <generation_instructions>
        <output_format>structured_legal_document</output_format>
        <required_sections>{required_sections}</required_sections>
        <style_guidelines>{style_guidelines}</style_guidelines>
        <jurisdiction_specific_rules>
            {jurisdiction_rules}
        </jurisdiction_specific_rules>
    </generation_instructions>
</petition_request>"""
    
    def build_prompt(self, state: Dict[str, Any]) -> str:
        """Build complete XML prompt from state"""
        try:
            # Extract case details
            case_details = state.get('case_details', {})
            
            # Get jurisdiction and petition type configs
            jurisdiction = state.get('jurisdiction')
            petition_type = state.get('petition_type')
            
            jurisdiction_config = JURISDICTION_CONFIG.get(jurisdiction, {})
            petition_config = PETITION_TYPE_CONFIG.get(petition_type, {})
            
            # Build structure templates section
            structure_templates = self._build_structure_templates(state.get('structure_chunks', []))
            
            # Build legal phrases section
            legal_phrases = self._build_legal_phrases(state.get('structure_chunks', []))
            
            # Build formatting rules
            formatting_rules = self._build_formatting_rules(jurisdiction, petition_type)
            
            # Build relevant cases section
            relevant_cases = self._build_relevant_cases(state.get('content_chunks', []))
            
            # Build legal arguments section
            legal_arguments = self._build_legal_arguments(state.get('content_chunks', []))
            
            # Build precedents section
            precedents = self._build_precedents(state.get('content_chunks', []))
            
            # Build jurisdiction-specific rules
            jurisdiction_rules = self._build_jurisdiction_rules(jurisdiction, petition_type)
            
            # Fill the template
            prompt = self.base_template.format(
                user_input=state.get('user_input', ''),
                jurisdiction=jurisdiction.value if jurisdiction else '',
                petition_type=petition_type.value if petition_type else '',
                petitioner=case_details.get('petitioner_name', ''),
                respondent=case_details.get('respondent_name', ''),
                incident_date=case_details.get('incident_date', ''),
                filing_date=case_details.get('filing_date', ''),
                case_number=case_details.get('case_number', 'Not specified'),
                structure_templates=structure_templates,
                legal_phrases=legal_phrases,
                formatting_rules=formatting_rules,
                relevant_cases=relevant_cases,
                legal_arguments=legal_arguments,
                precedents=precedents,
                required_sections=', '.join(jurisdiction_config.get('required_sections', [])),
                style_guidelines=petition_config.get('language', 'formal_legal'),
                jurisdiction_rules=jurisdiction_rules
            )
            
            return prompt
            
        except Exception as e:
            print(f"Error building XML prompt: {e}")
            return self._get_fallback_prompt(state)
    
    def _build_structure_templates(self, structure_chunks: List[Dict[str, Any]]) -> str:
        """Build structure templates section"""
        if not structure_chunks:
            return "<template>Standard legal document structure</template>"
        
        templates = []
        for chunk in structure_chunks[:3]:  # Top 3 structure chunks
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            
            template = f"""<template>
                <source>Case: {metadata.get('case_id', 'Unknown')}</source>
                <content>{content}</content>
            </template>"""
            templates.append(template)
        
        return '\n'.join(templates)
    
    def _build_legal_phrases(self, structure_chunks: List[Dict[str, Any]]) -> str:
        """Build legal phrases section"""
        if not structure_chunks:
            return "<phrase>Standard legal terminology</phrase>"
        
        phrases = set()
        for chunk in structure_chunks:
            metadata = chunk.get('metadata', {})
            legal_phrases = metadata.get('legal_phrases', [])
            phrases.update(legal_phrases)
        
        if not phrases:
            return "<phrase>Standard legal terminology</phrase>"
        
        phrase_elements = [f"<phrase>{phrase}</phrase>" for phrase in list(phrases)[:10]]
        return '\n'.join(phrase_elements)
    
    def _build_formatting_rules(self, jurisdiction: Jurisdiction, petition_type: PetitionType) -> str:
        """Build formatting rules section"""
        jurisdiction_config = JURISDICTION_CONFIG.get(jurisdiction, {})
        petition_config = PETITION_TYPE_CONFIG.get(petition_type, {})
        
        rules = []
        
        # Jurisdiction-specific formatting
        formatting = jurisdiction_config.get('formatting', 'standard')
        rules.append(f"<rule>Use {formatting} formatting style</rule>")
        
        # Petition type specific structure
        structure = petition_config.get('structure', 'standard')
        rules.append(f"<rule>Follow {structure} document structure</rule>")
        
        # Required sections
        required_sections = jurisdiction_config.get('required_sections', [])
        for section in required_sections:
            rules.append(f"<rule>Include {section} section</rule>")
        
        return '\n'.join(rules)
    
    def _build_relevant_cases(self, content_chunks: List[Dict[str, Any]]) -> str:
        """Build relevant cases section"""
        if not content_chunks:
            return "<case>No specific relevant cases found</case>"
        
        cases = []
        for chunk in content_chunks[:3]:  # Top 3 content chunks
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            
            case = f"""<case>
                <source>Case: {metadata.get('case_id', 'Unknown')}</source>
                <jurisdiction>{metadata.get('jurisdiction', 'Unknown')}</jurisdiction>
                <type>{metadata.get('petition_type', 'Unknown')}</type>
                <content>{content[:500]}...</content>
            </case>"""
            cases.append(case)
        
        return '\n'.join(cases)
    
    def _build_legal_arguments(self, content_chunks: List[Dict[str, Any]]) -> str:
        """Build legal arguments section"""
        if not content_chunks:
            return "<argument>Standard legal arguments based on facts</argument>"
        
        arguments = []
        for chunk in content_chunks:
            content = chunk.get('content', '')
            
            # Extract arguments from content
            if 'Arguments:' in content:
                arg_start = content.find('Arguments:') + len('Arguments:')
                arg_end = content.find('|', arg_start) if '|' in content[arg_start:] else len(content)
                argument_text = content[arg_start:arg_end].strip()
                
                if argument_text:
                    arguments.append(f"<argument>{argument_text[:300]}...</argument>")
        
        if not arguments:
            return "<argument>Standard legal arguments based on facts</argument>"
        
        return '\n'.join(arguments[:5])  # Top 5 arguments
    
    def _build_precedents(self, content_chunks: List[Dict[str, Any]]) -> str:
        """Build precedents section"""
        if not content_chunks:
            return "<precedent>Standard legal precedents</precedent>"
        
        precedents = set()
        for chunk in content_chunks:
            metadata = chunk.get('metadata', {})
            case_precedents = metadata.get('precedents', [])
            precedents.update(case_precedents)
        
        if not precedents:
            return "<precedent>Standard legal precedents</precedent>"
        
        precedent_elements = [f"<precedent>{precedent}</precedent>" for precedent in list(precedents)[:10]]
        return '\n'.join(precedent_elements)
    
    def _build_jurisdiction_rules(self, jurisdiction: Jurisdiction, petition_type: PetitionType) -> str:
        """Build jurisdiction-specific rules"""
        jurisdiction_config = JURISDICTION_CONFIG.get(jurisdiction, {})
        petition_config = PETITION_TYPE_CONFIG.get(petition_type, {})
        
        rules = []
        
        # Jurisdiction focus areas
        focus_areas = jurisdiction_config.get('focus', [])
        for focus in focus_areas:
            rules.append(f"<rule>Emphasize {focus} aspects</rule>")
        
        # Petition type focus areas
        petition_focus = petition_config.get('focus', [])
        for focus in petition_focus:
            rules.append(f"<rule>Include {focus} considerations</rule>")
        
        return '\n'.join(rules)
    
    def _get_fallback_prompt(self, state: Dict[str, Any]) -> str:
        """Get fallback prompt if XML building fails"""
        case_details = state.get('case_details', {})
        
        return f"""Generate a legal petition for the following case:

Jurisdiction: {state.get('jurisdiction', 'Unknown')}
Petition Type: {state.get('petition_type', 'Unknown')}
Petitioner: {case_details.get('petitioner_name', 'Unknown')}
Respondent: {case_details.get('respondent_name', 'Unknown')}
Facts: {case_details.get('facts', 'Not provided')}
Relief Sought: {case_details.get('relief', 'Not specified')}

Please generate a complete, professional legal petition with proper structure and formatting."""

class PromptValidator:
    """Validates XML prompts"""
    
    @staticmethod
    def validate_xml_structure(prompt: str) -> bool:
        """Validate basic XML structure"""
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(prompt)
            return True
        except ET.ParseError:
            return False
    
    @staticmethod
    def check_required_elements(prompt: str) -> List[str]:
        """Check for required XML elements"""
        required_elements = [
            'query_context',
            'retrieved_structure', 
            'retrieved_content',
            'generation_instructions'
        ]
        
        missing_elements = []
        for element in required_elements:
            if f"<{element}>" not in prompt or f"</{element}>" not in prompt:
                missing_elements.append(element)
        
        return missing_elements 