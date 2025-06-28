#!/usr/bin/env python3
"""
Petition Automator
==================

Automatically generates complete legal petitions using RAG system as reference.
The Ollama model writes the actual legal documents itself.
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.lawgorithm_rag_interface import LawgorithmRAGInterface

class PetitionAutomator:
    def __init__(self):
        """Initialize the petition automator"""
        print("🤖 Initializing Petition Automator...")
        
        try:
            self.rag = LawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
            print("✅ RAG system initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            sys.exit(1)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*70)
        print("📄 PETITION AUTOMATOR - LEGAL DOCUMENT GENERATOR")
        print("="*70)
        print("🎯 I automatically generate complete legal petitions using:")
        print("   • Your case details")
        print("   • Legal precedents from RAG system")
        print("   • Professional legal document structure")
        print("   • Proper legal language and formatting")
        print("\n💡 Just provide your case details and I'll write the petition!")
        print("="*70)
    
    def get_case_details(self):
        """Get comprehensive case details from user"""
        print("\n📋 CASE DETAILS COLLECTION")
        print("-" * 40)
        
        details = {}
        
        # Basic case information
        print("1️⃣ BASIC CASE INFORMATION")
        details['case_type'] = input("Case Type (e.g., Criminal, Civil, Family): ").strip()
        details['court'] = input("Court (e.g., Supreme Court, High Court): ").strip()
        details['petitioner_name'] = input("Petitioner Name: ").strip()
        details['respondent_name'] = input("Respondent Name: ").strip()
        
        print("\n2️⃣ CASE FACTS")
        details['incident_date'] = input("Date of Incident: ").strip()
        details['filing_date'] = input("Date of Filing: ").strip()
        details['case_number'] = input("Case Number (if any): ").strip()
        
        print("\n3️⃣ DETAILED FACTS")
        print("Describe what happened (be specific):")
        details['facts'] = input("Facts of the case: ").strip()
        
        print("\n4️⃣ EVIDENCE")
        print("What evidence do you have?")
        details['evidence'] = input("Evidence (documents, witnesses, etc.): ").strip()
        
        print("\n5️⃣ RELIEF SOUGHT")
        print("What do you want the court to do?")
        details['relief'] = input("Relief sought: ").strip()
        
        print("\n6️⃣ LEGAL GROUNDS")
        print("What legal provisions support your case?")
        details['legal_grounds'] = input("Legal grounds (sections, precedents): ").strip()
        
        return details
    
    def generate_petition(self, case_details):
        """Generate complete petition using RAG system"""
        print("\n🤖 Generating your legal petition...")
        
        # Create a better prompt that focuses on template-based generation
        prompt = f"""
CASE DETAILS TO FILL INTO PETITION TEMPLATE:

Case Type: {case_details['case_type']}
Court: {case_details['court']}
Petitioner: {case_details['petitioner_name']}
Respondent: {case_details['respondent_name']}
Incident Date: {case_details['incident_date']}
Filing Date: {case_details['filing_date']}
Case Number: {case_details['case_number']}

Facts of the Case: {case_details['facts']}

Evidence: {case_details['evidence']}

Relief Sought: {case_details['relief']}

Legal Grounds: {case_details['legal_grounds']}

Use these case details to fill in the petition template structure provided by the RAG system.
"""
        
        try:
            # Use RAG system to get relevant legal context
            rag_result = self.rag.query(prompt, top_k=2)
            
            if rag_result and 'response' in rag_result:
                petition = rag_result['response']
                print("✅ Petition generated successfully!")
                return petition
            else:
                return "Error: Could not generate petition. Please try again."
                
        except Exception as e:
            print(f"❌ Error generating petition: {e}")
            return f"Error generating petition: {str(e)}"
    
    def save_petition(self, case_details, petition_text):
        """Save the generated petition"""
        try:
            # Save as JSON with metadata
            json_filename = f"petition_{case_details['case_type'].lower()}_{self.session_id}.json"
            petition_data = {
                'session_id': self.session_id,
                'generated_at': datetime.now().isoformat(),
                'case_details': case_details,
                'petition_text': petition_text
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(petition_data, f, ensure_ascii=False, indent=2)
            
            # Save as clean text document
            text_filename = f"petition_{case_details['case_type'].lower()}_{self.session_id}.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write("LEGAL PETITION GENERATED BY PETITION AUTOMATOR\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Case Type: {case_details['case_type']}\n")
                f.write(f"Court: {case_details['court']}\n")
                f.write(f"Petitioner: {case_details['petitioner_name']}\n")
                f.write(f"Respondent: {case_details['respondent_name']}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("=" * 60 + "\n\n")
                f.write(petition_text)
            
            print(f"\n💾 Petition saved to: {json_filename}")
            print(f"📄 Petition also saved as text: {text_filename}")
            
        except Exception as e:
            print(f"❌ Error saving petition: {e}")
    
    def review_and_edit_petition(self, case_details, initial_petition):
        """Allow user to review and edit the generated petition"""
        while True:
            print("\n" + "="*70)
            print("📄 PETITION REVIEW")
            print("="*70)
            
            # Clean up the petition text if it's in JSON format
            if isinstance(initial_petition, str):
                # Try to extract text from JSON if it's wrapped in JSON
                if initial_petition.strip().startswith('{'):
                    try:
                        import json
                        petition_data = json.loads(initial_petition)
                        if 'response' in petition_data:
                            clean_petition = petition_data['response']
                        else:
                            clean_petition = initial_petition
                    except:
                        clean_petition = initial_petition
                else:
                    clean_petition = initial_petition
            else:
                clean_petition = str(initial_petition)
            
            # Display the clean petition text
            print(clean_petition)
            print("="*70)
            
            print("\n🤔 Are you happy with this petition?")
            print("1. Yes - Save and finish")
            print("2. No - I want changes")
            print("3. Regenerate completely")
            print("4. Exit without saving")
            
            choice = input("\n🔍 Enter your choice (1-4): ").strip()
            
            if choice == '1':
                # User is happy - save and finish
                self.save_petition(case_details, clean_petition)
                print("✅ Petition saved successfully!")
                return True
                
            elif choice == '2':
                # User wants changes
                print("\n📝 What changes would you like to make?")
                print("💡 Be specific about what you want to change:")
                print("   • Add more details to facts")
                print("   • Change legal arguments")
                print("   • Modify relief sought")
                print("   • Add/remove sections")
                print("   • Change language or tone")
                print("   • Any other modifications")
                
                changes = input("\n📝 Describe the changes you want: ").strip()
                
                if changes.lower() in ['quit', 'exit', 'cancel']:
                    continue
                
                if len(changes) < 10:
                    print("❌ Please provide more specific details about the changes.")
                    continue
                
                # Generate updated petition with changes
                print("\n🤖 Generating updated petition with your changes...")
                updated_petition = self.generate_updated_petition(case_details, clean_petition, changes)
                
                if updated_petition and updated_petition != clean_petition:
                    initial_petition = updated_petition
                    print("✅ Petition updated! Let's review the new version.")
                else:
                    print("❌ Could not update petition. Please try again with different instructions.")
                
            elif choice == '3':
                # Regenerate completely
                print("\n🔄 Regenerating petition completely...")
                new_petition = self.generate_petition(case_details)
                if new_petition and new_petition != "Error":
                    initial_petition = new_petition
                    print("✅ New petition generated! Let's review it.")
                else:
                    print("❌ Could not regenerate petition. Please try again.")
                
            elif choice == '4':
                # Exit without saving
                print("👋 Exiting without saving. Goodbye!")
                return False
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
    
    def generate_updated_petition(self, case_details, original_petition, changes_requested):
        """Generate updated petition based on user's requested changes"""
        print("🔍 Searching legal precedents for updates...")
        
        # Create a better prompt for applying changes
        prompt = f"""
ORIGINAL PETITION:
{original_petition}

REQUESTED CHANGES:
{changes_requested}

CASE DETAILS:
Case Type: {case_details['case_type']}
Court: {case_details['court']}
Petitioner: {case_details['petitioner_name']}
Respondent: {case_details['respondent_name']}

INSTRUCTIONS:
Apply the requested changes to the original petition while maintaining:
1. The same overall structure and format
2. Proper legal language and terminology
3. All case details and facts
4. Professional petition formatting

Make ONLY the specific changes requested and keep everything else the same.
"""
        
        try:
            # Use RAG system to get relevant legal context for updates
            rag_result = self.rag.query(prompt, top_k=3)
            
            if rag_result and 'response' in rag_result:
                updated_petition = rag_result['response']
                print("✅ Petition updated successfully!")
                return updated_petition
            else:
                return "Error: Could not update petition. Please try again."
                
        except Exception as e:
            print(f"❌ Error updating petition: {e}")
            return f"Error updating petition: {str(e)}"
    
    def start_automation(self):
        """Start the petition automation process"""
        self.display_welcome()
        
        while True:
            try:
                print("\n🎯 Ready to generate your legal petition!")
                choice = input("Start new petition? (y/n): ").strip().lower()
                
                if choice not in ['y', 'yes']:
                    print("👋 Thank you for using Petition Automator!")
                    break
                
                # Get case details
                case_details = self.get_case_details()
                
                # Generate initial petition
                petition_text = self.generate_petition(case_details)
                
                if petition_text and petition_text != "Error":
                    # Review and edit the petition
                    self.review_and_edit_petition(case_details, petition_text)
                else:
                    print("❌ Failed to generate petition. Please try again.")
                
                # Ask if user wants to generate another petition
                continue_choice = input("\nGenerate another petition? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Thank you for using Petition Automator!")
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 Petition automation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.\n")

def main():
    """Main function"""
    automator = PetitionAutomator()
    automator.start_automation()

if __name__ == "__main__":
    main() 