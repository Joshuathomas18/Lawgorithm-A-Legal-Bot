#!/usr/bin/env python3
"""
Petition Service
===============

Service for generating legal petitions and documents.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from models.database import PetitionRepository

logger = logging.getLogger(__name__)

class PetitionService:
    def __init__(self, rag_service=None, gemini_service=None):
        self.rag_service = rag_service
        self.gemini_service = gemini_service
        self.is_initialized = True
        
    async def generate_petition(self, session_id: str, case_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a legal petition based on case details"""
        try:
            logger.info(f"📜 Generating petition for session {session_id}")
            
            # Extract case information
            case_type = case_details.get('type', 'general')
            case_facts = case_details.get('facts', '')
            relief_sought = case_details.get('relief', '')
            
            # Generate petition using AI
            petition_text = await self._generate_petition_text(case_type, case_facts, relief_sought)
            
            # Create petition record
            petition_id = str(uuid.uuid4())
            success = await PetitionRepository.create_petition(
                petition_id=petition_id,
                session_id=session_id,
                case_details=case_details,
                petition_text=petition_text
            )
            
            if success:
                return {
                    'petition_id': petition_id,
                    'petition_text': petition_text,
                    'case_details': case_details,
                    'generated_at': datetime.now().isoformat(),
                    'status': 'generated'
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating petition: {e}")
            return None
    
    async def _generate_petition_text(self, case_type: str, case_facts: str, relief_sought: str) -> str:
        """Generate petition text using AI"""
        try:
            if self.gemini_service and self.gemini_service.is_initialized:
                # Create prompt for petition generation
                prompt = f"""
                Generate a comprehensive legal petition for the Indian legal system based on the following details:

                Case Type: {case_type}
                Case Facts: {case_facts}
                Relief Sought: {relief_sought}

                Please create a complete petition that includes:
                1. Proper legal heading with court name placeholder
                2. Parties section (petitioner and respondent)
                3. Detailed facts section
                4. Legal arguments and grounds
                5. Prayer section with specific relief sought
                6. Proper legal conclusion and affidavit

                Format the petition according to Indian legal standards with proper legal language and structure.
                
                Important: Do not include verification section.
                """
                
                petition_text = await self.gemini_service.generate_complete_document(prompt, "petition")
                
                if petition_text:
                    return petition_text
                else:
                    return self._generate_template_petition(case_type, case_facts, relief_sought)
            else:
                return self._generate_template_petition(case_type, case_facts, relief_sought)
                
        except Exception as e:
            logger.error(f"❌ Error generating petition text: {e}")
            return self._generate_template_petition(case_type, case_facts, relief_sought)
    
    def _generate_template_petition(self, case_type: str, case_facts: str, relief_sought: str) -> str:
        """Generate template-based petition when AI is not available"""
        return f"""
IN THE COURT OF [COURT NAME]
[CASE NUMBER]

PETITION UNDER [RELEVANT LEGAL PROVISION]

BETWEEN:

[PETITIONER NAME]
[PETITIONER ADDRESS]
                                                    - Petitioner

AND

[RESPONDENT NAME]  
[RESPONDENT ADDRESS]
                                                    - Respondent

MOST RESPECTFULLY SHEWETH:

1. That the petitioner is a law-abiding citizen of India and has approached this Hon'ble Court seeking justice in the matter described hereinafter.

2. That the facts of the case are as follows:
{case_facts}

3. That the petitioner submits that the above-mentioned facts constitute a clear case for the relief sought herein.

4. That the petitioner has no other efficacious remedy available except to approach this Hon'ble Court.

5. That this petition is being filed within the prescribed limitation period.

GROUNDS:

A. That the petitioner has made out a prima facie case for the relief sought.

B. That the balance of convenience lies in favor of the petitioner.

C. That irreparable harm and injury would be caused to the petitioner if the relief is not granted.

PRAYER:

In the premises aforesaid, it is most respectfully prayed that this Hon'ble Court may be pleased to:

a) {relief_sought}
b) Pass such other orders as this Hon'ble Court may deem fit and proper in the circumstances of the case.
c) Award costs of this petition.

And for this act of kindness, the petitioner shall ever pray.

[PLACE]                                           [PETITIONER/ADVOCATE SIGNATURE]
[DATE]

AFFIDAVIT

I, [PETITIONER NAME], do hereby solemnly affirm and declare as under:

1. That I am the petitioner in the above-styled case and as such I am conversant with the facts and circumstances of the case.

2. That I have read over the contents of the above petition and the same are true and correct to the best of my knowledge and belief and nothing material has been concealed therefrom.

3. That the petition is filed with bona fide intention and not for any collateral purpose.

Deponent

[PETITIONER SIGNATURE]

**Legal Disclaimer**: This is a template petition. Please consult with a qualified lawyer for review and customization according to your specific case requirements and applicable laws.
"""
    
    async def get_petition(self, petition_id: str) -> Optional[Dict[str, Any]]:
        """Get petition by ID"""
        try:
            return await PetitionRepository.get_petition(petition_id)
        except Exception as e:
            logger.error(f"❌ Error getting petition: {e}")
            return None
    
    async def update_petition(self, petition_id: str, petition_text: str, changes_made: str) -> bool:
        """Update petition with new version"""
        try:
            return await PetitionRepository.update_petition(petition_id, petition_text, changes_made)
        except Exception as e:
            logger.error(f"❌ Error updating petition: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for petition service"""
        return {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'rag_service_available': self.rag_service is not None and self.rag_service.is_initialized,
            'gemini_service_available': self.gemini_service is not None and self.gemini_service.is_initialized
        }