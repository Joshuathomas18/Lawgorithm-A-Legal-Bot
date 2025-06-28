#!/usr/bin/env python3
"""
Petition Service
================

Service for handling petition generation and management.
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..models.database import PetitionRepository
from ..models.schemas import CaseDetails

logger = logging.getLogger(__name__)

class PetitionService:
    def __init__(self, rag_service, gemini_service):
        self.rag_service = rag_service
        self.gemini_service = gemini_service
        
    async def generate_petition(self, case_details: CaseDetails, session_id: str) -> Optional[Dict[str, Any]]:
        """Generate a complete petition using RAG and Gemini"""
        try:
            logger.info(f"📄 Generating petition for session: {session_id}")
            
            # Create comprehensive prompt for petition generation
            prompt = self._create_petition_prompt(case_details)
            
            # Get legal precedents from RAG
            precedents = await self.rag_service.get_legal_precedents(
                case_details.case_type.value,
                case_details.court.value,
                [case_details.facts, case_details.evidence, case_details.relief]
            )
            
            # Combine precedents with prompt
            context = self._format_precedents(precedents)
            full_prompt = f"{prompt}\n\nLEGAL PRECEDENTS:\n{context}"
            
            # Generate petition using Gemini
            petition_text = await self.gemini_service.generate_text(full_prompt)
            
            if not petition_text:
                logger.error("❌ Failed to generate petition text")
                return None
            
            # Create petition record
            petition_id = str(uuid.uuid4())
            case_details_dict = case_details.dict()
            
            # Save to database
            success = await PetitionRepository.create_petition(
                petition_id, session_id, case_details_dict, petition_text
            )
            
            if not success:
                logger.error("❌ Failed to save petition to database")
                return None
            
            return {
                'petition_id': petition_id,
                'petition_text': petition_text,
                'case_details': case_details_dict,
                'generated_at': datetime.now().isoformat(),
                'session_id': session_id,
                'status': 'generated',
                'precedents_used': len(precedents)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating petition: {e}")
            return None
    
    async def update_petition(self, petition_id: str, changes_requested: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing petition based on requested changes"""
        try:
            logger.info(f"📝 Updating petition: {petition_id}")
            
            # Get original petition
            original_petition = await PetitionRepository.get_petition(petition_id)
            if not original_petition:
                logger.error(f"❌ Petition not found: {petition_id}")
                return None
            
            # Create update prompt
            update_prompt = self._create_update_prompt(
                original_petition['case_details'],
                original_petition['petition_text'],
                changes_requested
            )
            
            # Get relevant precedents for updates
            precedents = await self.rag_service.get_legal_precedents(
                original_petition['case_details']['case_type'],
                original_petition['case_details']['court'],
                [changes_requested]
            )
            
            # Combine with prompt
            context = self._format_precedents(precedents)
            full_prompt = f"{update_prompt}\n\nLEGAL PRECEDENTS:\n{context}"
            
            # Generate updated petition
            updated_text = await self.gemini_service.generate_text(full_prompt)
            
            if not updated_text:
                logger.error("❌ Failed to generate updated petition")
                return None
            
            # Update in database
            success = await PetitionRepository.update_petition(
                petition_id, updated_text, changes_requested
            )
            
            if not success:
                logger.error("❌ Failed to update petition in database")
                return None
            
            return {
                'petition_id': petition_id,
                'updated_petition_text': updated_text,
                'changes_made': changes_requested,
                'updated_at': datetime.now().isoformat(),
                'precedents_used': len(precedents)
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating petition: {e}")
            return None
    
    async def get_petition(self, petition_id: str) -> Optional[Dict[str, Any]]:
        """Get petition by ID"""
        try:
            return await PetitionRepository.get_petition(petition_id)
        except Exception as e:
            logger.error(f"❌ Error getting petition: {e}")
            return None
    
    def _create_petition_prompt(self, case_details: CaseDetails) -> str:
        """Create comprehensive prompt for petition generation"""
        return f"""
Generate a complete, professional legal petition for the following case:

CASE DETAILS:
- Case Type: {case_details.case_type.value}
- Court: {case_details.court.value}
- Petitioner: {case_details.petitioner_name}
- Respondent: {case_details.respondent_name}
- Incident Date: {case_details.incident_date}
- Filing Date: {case_details.filing_date}
- Case Number: {case_details.case_number or 'Not specified'}

FACTS OF THE CASE:
{case_details.facts}

EVIDENCE:
{case_details.evidence}

RELIEF SOUGHT:
{case_details.relief}

LEGAL GROUNDS:
{case_details.legal_grounds}

INSTRUCTIONS:
Write a complete, professional legal petition that includes:
1. Proper court heading and case title
2. Introduction and jurisdiction
3. Statement of facts
4. Legal arguments with relevant sections
5. Prayer for relief
6. Verification clause
7. Proper legal language and formatting

Make this a complete, ready-to-file legal document suitable for {case_details.court.value}.
"""
    
    def _create_update_prompt(self, case_details: Dict, original_petition: str, changes_requested: str) -> str:
        """Create prompt for updating existing petition"""
        return f"""
I have an existing legal petition that needs to be updated. Here are the details:

ORIGINAL CASE DETAILS:
- Case Type: {case_details['case_type']}
- Court: {case_details['court']}
- Petitioner: {case_details['petitioner_name']}
- Respondent: {case_details['respondent_name']}

ORIGINAL PETITION:
{original_petition}

REQUESTED CHANGES:
{changes_requested}

INSTRUCTIONS:
Please generate an updated version of the petition that incorporates the requested changes while maintaining:
1. Professional legal language and structure
2. All necessary legal sections
3. Proper formatting and court requirements
4. Consistency with the original case details

Make the requested changes and provide the complete updated petition.
"""
    
    def _format_precedents(self, precedents: List[Dict[str, Any]]) -> str:
        """Format legal precedents for inclusion in prompt"""
        if not precedents:
            return "No specific precedents found."
        
        formatted = []
        for i, precedent in enumerate(precedents[:3], 1):  # Limit to top 3
            doc = precedent.get('document', '')
            metadata = precedent.get('metadata', {})
            similarity = precedent.get('similarity', 0)
            
            formatted.append(f"Precedent {i} (Relevance: {similarity:.2f}):")
            formatted.append(f"Source: {metadata.get('court', 'Unknown Court')} - {metadata.get('date', 'Unknown Date')}")
            formatted.append(f"Content: {doc[:500]}...")
            formatted.append("")
        
        return "\n".join(formatted) 