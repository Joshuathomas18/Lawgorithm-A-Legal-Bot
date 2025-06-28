#!/usr/bin/env python3
"""
Structured Petition Generator
============================

A guided system for creating legal petitions step-by-step.
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lawgorithm_rag_interface import LawgorithmRAGInterface

class StructuredPetitionGenerator:
    def __init__(self):
        vector_store_path = os.path.join(os.path.dirname(__file__), "vector_store_lawgorithm", "vector_store.json")
        self.rag = LawgorithmRAGInterface(vector_store_path)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Case types and courts
        self.case_types = [
            "criminal", "civil", "family", "constitutional", 
            "environmental", "commercial", "tax", "labor",
            "consumer", "property", "contract", "tort"
        ]
        
        self.courts = [
            "Supreme Court", "High Court", "District Court", 
            "Magistrate Court", "Consumer Court", "Family Court", 
            "Labor Court", "Commercial Court", "Tribunal"
        ]
        
        # Current petition data
        self.current_petition = {
            'case_type': None,
            'court': None,
            'brief_details': None,
            'plan_of_action': None,
            'specific_details': None,
            'final_petition': None,
            'created_at': datetime.now().isoformat()
        }
    
    def test_rag_connection(self):
        """Test RAG connection and display status"""
        print("🔍 Testing RAG System Connection...")
        try:
            # Test if RAG system is working
            test_query = "test connection"
            result = self.rag.query(test_query, top_k=1)
            
            if result and 'total_sources' in result:
                print(f"✅ RAG System Connected! Found {result['total_sources']} legal documents")
                return True
            else:
                print("❌ RAG System not responding properly")
                return False
        except Exception as e:
            print(f"❌ RAG System Error: {e}")
            return False
    
    def display_welcome(self):
        """Display welcome message"""
        print("🤖 Welcome to Structured Petition Generator!")
        print("=" * 50)
        print("📋 I'll guide you through creating a legal petition step-by-step.")
        print("💡 This system will help you:")
        print("   • Choose the right case type and court")
        print("   • Structure your petition properly")
        print("   • Get legal guidance and precedents")
        print("   • Edit and refine your petition")
        print("\n🔄 You can go back and edit any step at any time.")
        print("📝 Type 'quit' to exit.")
        
        # Test RAG connection
        self.test_rag_connection()
        print()
    
    def get_case_type(self) -> str:
        """Get case type from user"""
        print("📋 STEP 1: Select Case Type")
        print("-" * 30)
        print("Available case types:")
        
        for i, case_type in enumerate(self.case_types, 1):
            print(f"   {i}. {case_type.title()}")
        
        while True:
            try:
                choice = input("\n🔍 Enter case type (number or name): ").strip().lower()
                
                if choice in ['quit', 'q']:
                    return 'quit'
                
                # Try number input
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.case_types):
                        selected_type = self.case_types[idx]
                        print(f"✅ Selected case type: {selected_type.title()}")
                        return selected_type
                    else:
                        print("❌ Invalid number. Please try again.")
                        continue
                
                # Try name input
                for case_type in self.case_types:
                    if choice in case_type.lower():
                        print(f"✅ Selected case type: {case_type.title()}")
                        return case_type
                
                print("❌ Invalid case type. Please try again.")
                
            except KeyboardInterrupt:
                return 'quit'
    
    def get_court(self) -> str:
        """Get court from user"""
        print("\n📋 STEP 2: Select Court")
        print("-" * 30)
        print("Available courts:")
        
        for i, court in enumerate(self.courts, 1):
            print(f"   {i}. {court}")
        
        while True:
            try:
                choice = input("\n🔍 Enter court (number or name): ").strip()
                
                if choice.lower() in ['quit', 'q']:
                    return 'quit'
                
                # Try number input
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.courts):
                        selected_court = self.courts[idx]
                        print(f"✅ Selected court: {selected_court}")
                        return selected_court
                    else:
                        print("❌ Invalid number. Please try again.")
                        continue
                
                # Try name input
                for court in self.courts:
                    if choice.lower() in court.lower():
                        print(f"✅ Selected court: {court}")
                        return court
                
                print("❌ Invalid court. Please try again.")
                
            except KeyboardInterrupt:
                return 'quit'
    
    def get_brief_details(self) -> str:
        """Get brief details from user"""
        print("\n📋 STEP 3: Brief Details")
        print("-" * 30)
        print("💡 Provide a brief overview of your case:")
        print("   • What happened?")
        print("   • Who are the parties involved?")
        print("   • What relief are you seeking?")
        print("   • Any key dates or deadlines?")
        
        while True:
            try:
                details = input("\n📝 Enter brief details: ").strip()
                
                if details.lower() in ['quit', 'q']:
                    return 'quit'
                
                if len(details) < 10:
                    print("❌ Please provide more details (at least 10 characters).")
                    continue
                
                print(f"✅ Brief details recorded: {details[:100]}...")
                return details
                
            except KeyboardInterrupt:
                return 'quit'
    
    def generate_plan_of_action(self) -> str:
        """Generate plan of action using RAG system"""
        print("\n📋 STEP 4: Generating Plan of Action")
        print("-" * 40)
        print("🤔 Analyzing your case and generating a plan...")
        
        try:
            # Create query for RAG system
            query = f"Generate a plan of action for a {self.current_petition['case_type']} case in {self.current_petition['court']}. Case details: {self.current_petition['brief_details']}"
            
            print("🔍 Searching legal knowledge base...")
            
            # Use RAG system to get legal context and generate plan
            rag_result = self.rag.query(query, top_k=3)
            
            if rag_result and 'response' in rag_result:
                plan = rag_result['response']
                print("✅ Plan of action generated successfully using RAG!")
                return plan
            else:
                return "Unable to generate plan at this time. Please proceed with manual planning."
                
        except Exception as e:
            print(f"❌ Error generating plan: {e}")
            return "Error generating plan. Please proceed with manual planning."
    
    def get_specific_details(self) -> str:
        """Get specific details based on plan"""
        print("\n📋 STEP 5: Specific Details")
        print("-" * 30)
        print("💡 Based on the plan, provide specific details:")
        print("   • Names of all parties")
        print("   • Specific dates and events")
        print("   • Evidence you have")
        print("   • Witnesses (if any)")
        print("   • Previous legal proceedings")
        print("   • Any other relevant information")
        
        while True:
            try:
                details = input("\n📝 Enter specific details: ").strip()
                
                if details.lower() in ['quit', 'q']:
                    return 'quit'
                
                if len(details) < 20:
                    print("❌ Please provide more specific details (at least 20 characters).")
                    continue
                
                print(f"✅ Specific details recorded: {details[:100]}...")
                return details
                
            except KeyboardInterrupt:
                return 'quit'
    
    def generate_final_petition(self) -> str:
        """Generate final petition using RAG system"""
        print("\n📋 STEP 6: Generating Final Petition")
        print("-" * 40)
        print("🤖 Creating your final petition...")
        
        try:
            # Create comprehensive query for RAG system
            query = f"Generate a complete {self.current_petition['case_type']} petition for {self.current_petition['court']}. Brief details: {self.current_petition['brief_details']}. Specific details: {self.current_petition['specific_details']}"
            
            print("🔍 Searching legal knowledge base...")
            
            # Use RAG system to get legal context and generate petition
            rag_result = self.rag.query(query, top_k=5)
            
            if rag_result and 'response' in rag_result:
                petition = rag_result['response']
                print("✅ Final petition generated successfully using RAG!")
                return petition
            else:
                return "Unable to generate petition at this time. Please try again."
                
        except Exception as e:
            print(f"❌ Error generating petition: {e}")
            return "Error generating petition. Please try again."
    
    def edit_petition(self) -> str:
        """Allow user to edit the petition"""
        print("\n📋 EDITING OPTIONS")
        print("-" * 30)
        print("What would you like to edit?")
        print("1. Case type")
        print("2. Court")
        print("3. Brief details")
        print("4. Plan of action")
        print("5. Specific details")
        print("6. Regenerate final petition")
        print("7. Save and exit")
        print("8. Start over")
        
        while True:
            try:
                choice = input("\n🔍 Enter your choice (1-8): ").strip()
                
                if choice == '1':
                    self.current_petition['case_type'] = self.get_case_type()
                    if self.current_petition['case_type'] == 'quit':
                        return 'quit'
                elif choice == '2':
                    self.current_petition['court'] = self.get_court()
                    if self.current_petition['court'] == 'quit':
                        return 'quit'
                elif choice == '3':
                    self.current_petition['brief_details'] = self.get_brief_details()
                    if self.current_petition['brief_details'] == 'quit':
                        return 'quit'
                elif choice == '4':
                    self.current_petition['plan_of_action'] = self.generate_plan_of_action()
                elif choice == '5':
                    self.current_petition['specific_details'] = self.get_specific_details()
                    if self.current_petition['specific_details'] == 'quit':
                        return 'quit'
                elif choice == '6':
                    self.current_petition['final_petition'] = self.generate_final_petition()
                elif choice == '7':
                    return 'save'
                elif choice == '8':
                    return 'restart'
                else:
                    print("❌ Invalid choice. Please enter 1-8.")
                    continue
                
                print("\n✅ Edit completed! What would you like to do next?")
                
            except KeyboardInterrupt:
                return 'quit'
    
    def save_petition(self):
        """Save petition to file"""
        try:
            filename = f"petition_{self.current_petition['case_type']}_{self.session_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.current_petition, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Petition saved to: {filename}")
            
            # Also save as text file
            text_filename = f"petition_{self.current_petition['case_type']}_{self.session_id}.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write("PETITION GENERATED BY LAWGORITHM RAG\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Case Type: {self.current_petition['case_type']}\n")
                f.write(f"Court: {self.current_petition['court']}\n")
                f.write(f"Created: {self.current_petition['created_at']}\n\n")
                f.write("BRIEF DETAILS:\n")
                f.write(self.current_petition['brief_details'] + "\n\n")
                f.write("PLAN OF ACTION:\n")
                f.write(self.current_petition['plan_of_action'] + "\n\n")
                f.write("SPECIFIC DETAILS:\n")
                f.write(self.current_petition['specific_details'] + "\n\n")
                f.write("FINAL PETITION:\n")
                f.write(self.current_petition['final_petition'] + "\n")
            
            print(f"📄 Petition also saved as text: {text_filename}")
            
        except Exception as e:
            print(f"❌ Error saving petition: {e}")
    
    def show_summary(self):
        """Show current petition summary"""
        print("\n📋 CURRENT PETITION SUMMARY")
        print("=" * 40)
        print(f"Case Type: {self.current_petition['case_type']}")
        print(f"Court: {self.current_petition['court']}")
        print(f"Brief Details: {self.current_petition['brief_details'][:100]}...")
        print(f"Plan Generated: {'Yes' if self.current_petition['plan_of_action'] else 'No'}")
        print(f"Specific Details: {'Yes' if self.current_petition['specific_details'] else 'No'}")
        print(f"Final Petition: {'Yes' if self.current_petition['final_petition'] else 'No'}")
    
    def start_generation(self):
        """Start the petition generation process"""
        self.display_welcome()
        
        while True:
            try:
                # Step 1: Get case type
                if not self.current_petition['case_type']:
                    self.current_petition['case_type'] = self.get_case_type()
                    if self.current_petition['case_type'] == 'quit':
                        break
                
                # Step 2: Get court
                if not self.current_petition['court']:
                    self.current_petition['court'] = self.get_court()
                    if self.current_petition['court'] == 'quit':
                        break
                
                # Step 3: Get brief details
                if not self.current_petition['brief_details']:
                    self.current_petition['brief_details'] = self.get_brief_details()
                    if self.current_petition['brief_details'] == 'quit':
                        break
                
                # Step 4: Generate plan of action
                if not self.current_petition['plan_of_action']:
                    self.current_petition['plan_of_action'] = self.generate_plan_of_action()
                    print(f"\n📋 PLAN OF ACTION:\n{self.current_petition['plan_of_action']}")
                
                # Step 5: Get specific details
                if not self.current_petition['specific_details']:
                    self.current_petition['specific_details'] = self.get_specific_details()
                    if self.current_petition['specific_details'] == 'quit':
                        break
                
                # Step 6: Generate final petition
                if not self.current_petition['final_petition']:
                    self.current_petition['final_petition'] = self.generate_final_petition()
                    print(f"\n📋 FINAL PETITION:\n{self.current_petition['final_petition']}")
                
                # Show summary and offer editing
                self.show_summary()
                
                # Offer editing options
                print("\n🎯 Petition generation complete!")
                choice = input("Would you like to edit anything? (y/n): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    result = self.edit_petition()
                    if result == 'save':
                        self.save_petition()
                        break
                    elif result == 'restart':
                        self.current_petition = {
                            'case_type': None,
                            'court': None,
                            'brief_details': None,
                            'plan_of_action': None,
                            'specific_details': None,
                            'final_petition': None,
                            'created_at': datetime.now().isoformat()
                        }
                        continue
                    elif result == 'quit':
                        break
                else:
                    self.save_petition()
                
                # Enter continuous conversation mode
                self.continuous_conversation_mode()
                break
                
            except KeyboardInterrupt:
                print("\n\n👋 Petition generation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.\n")

    def continuous_conversation_mode(self):
        """Keep the conversation going after petition generation"""
        print("\n" + "="*60)
        print("🤖 CONTINUOUS CONVERSATION MODE")
        print("="*60)
        print("💡 You can now:")
        print("   • Ask legal questions")
        print("   • Generate a new petition")
        print("   • Get legal advice")
        print("   • Discuss your case")
        print("   • Type 'quit' to exit")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using Lawgorithm RAG! Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Check for special commands
                if user_input.lower().startswith('new petition'):
                    print("\n🔄 Starting new petition generation...")
                    self.current_petition = {
                        'case_type': None,
                        'court': None,
                        'brief_details': None,
                        'plan_of_action': None,
                        'specific_details': None,
                        'final_petition': None,
                        'created_at': datetime.now().isoformat()
                    }
                    self.start_generation()
                    break
                
                if user_input.lower().startswith('save'):
                    self.save_petition()
                    print("✅ Current petition saved!")
                    continue
                
                if user_input.lower().startswith('summary'):
                    self.show_summary()
                    continue
                
                # Use RAG system to answer the question
                print("\n🤖 Lawgorithm: Thinking...")
                try:
                    rag_result = self.rag.query(user_input, top_k=3)
                    if rag_result and 'response' in rag_result:
                        print(f"\n🤖 Lawgorithm: {rag_result['response']}")
                    else:
                        print("\n🤖 Lawgorithm: I'm sorry, I couldn't generate a response for that question.")
                except Exception as e:
                    print(f"\n🤖 Lawgorithm: I encountered an error: {e}")
                    print("Please try rephrasing your question.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error in conversation: {e}")
                print("Please try again.")

def main():
    """Main function"""
    generator = StructuredPetitionGenerator()
    generator.start_generation()

if __name__ == "__main__":
    main() 