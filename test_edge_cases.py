#!/usr/bin/env python3
"""
Test script to verify edge cases in diagram generation and ensure robust relationship handling.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.diagram_service import DiagramService

async def test_edge_cases():
    """Test edge cases that might break relationship generation"""
    
    print("Testing diagram generation edge cases...")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Minimal Requirements",
            "snl": "User logs into system. System validates user.",
            "actors": ["User", "System"]
        },
        {
            "name": "Complex Domain",
            "snl": """Hospital management system handles patient records.
            Doctors can view patient information and update medical records.
            Nurses can schedule appointments and update patient status.
            Patients can view their medical history and book appointments.
            Administrators manage user accounts and system settings.
            The billing system generates invoices for treatments.""",
            "actors": ["Doctor", "Nurse", "Patient", "Administrator", "BillingSystem"]
        },
        {
            "name": "E-commerce System",
            "snl": """Online shopping platform allows customers to browse products.
            Customers can add items to cart and make purchases.
            Sellers can list products and manage inventory.
            Payment gateway processes transactions securely.
            Order management system tracks delivery status.
            Customer service handles inquiries and returns.""",
            "actors": ["Customer", "Seller", "PaymentGateway", "OrderManager", "CustomerService"]
        }
    ]
    
    try:
        diagram_service = DiagramService()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print("-" * 50)
            print(f"SNL: {test_case['snl'][:100]}...")
            print(f"Expected actors: {test_case['actors']}")
            
            # Generate initial diagrams
            class_diagram = await diagram_service.generate_class_diagram_from_rupp(test_case['snl'])
            sequence_diagram = await diagram_service.generate_sequence_diagram_from_rupp(test_case['snl'])
            
            # Extract actors
            extracted_actors = await diagram_service.extract_actors_from_requirements(
                test_case['snl'], class_diagram, sequence_diagram
            )
            
            # Verify diagrams
            verification = await diagram_service.verify_diagrams_with_actors(
                class_diagram, sequence_diagram, test_case['actors']
            )
            
            # Optimize diagrams
            optimization = await diagram_service.optimize_diagrams_with_llm_and_actors(
                test_case['snl'], class_diagram, sequence_diagram, test_case['actors'], verification
            )
            
            # Analyze relationships
            class_rels = count_relationships(optimization['class_diagram'])
            seq_ints = count_interactions(optimization['sequence_diagram'])
            
            # Check for undefined references
            undefined_refs = check_undefined_references(optimization['class_diagram'])
            
            print(f"Extracted actors: {extracted_actors[:5]}...")  # Show first 5
            print(f"Actor coverage: {verification['overall_score']:.2%}")
            print(f"Class relationships: {class_rels}")
            print(f"Sequence interactions: {seq_ints}")
            print(f"Undefined references: {undefined_refs}")
            
            # Validate results
            issues = []
            if class_rels == 0:
                issues.append("No class relationships")
            if seq_ints == 0:
                issues.append("No sequence interactions")
            if undefined_refs:
                issues.append(f"Undefined references: {undefined_refs}")
            if verification['overall_score'] < 0.8:
                issues.append(f"Low actor coverage: {verification['overall_score']:.2%}")
            
            if issues:
                print(f"⚠️  Issues: {', '.join(issues)}")
            else:
                print("✅ All checks passed!")
                
    except Exception as e:
        print(f"\n❌ ERROR during edge case testing: {str(e)}")
        import traceback
        traceback.print_exc()

def count_relationships(class_diagram: str) -> int:
    """Count relationship indicators in class diagram"""
    indicators = ['-->', '--', '..>', '..', '|>', '<|--', 'extends', 'implements', 'uses', 'borrows', 'manages', 'contains', 'has', 'owns', 'creates']
    count = 0
    for indicator in indicators:
        count += class_diagram.count(indicator)
    return count

def count_interactions(sequence_diagram: str) -> int:
    """Count interaction indicators in sequence diagram"""
    indicators = ['->', '-->', '->>', '<-', '<--', '<->']
    count = 0
    for indicator in indicators:
        count += sequence_diagram.count(indicator)
    return count

def check_undefined_references(class_diagram: str) -> list:
    """Check for undefined class references in relationships"""
    lines = class_diagram.split('\n')
    defined_classes = set()
    referenced_classes = set()
    
    # Find defined classes
    for line in lines:
        line = line.strip()
        if line.startswith('class '):
            class_name = line.split()[1].split('{')[0].strip()
            defined_classes.add(class_name)
    
    # Find referenced classes in relationships
    for line in lines:
        line = line.strip()
        if any(rel in line for rel in ['--', '->', '..', '|>', '<|']):
            # Extract class names from relationship line
            parts = line.split()
            for part in parts:
                if part and part.isalpha() and part[0].isupper():
                    referenced_classes.add(part)
    
    # Find undefined references
    undefined = referenced_classes - defined_classes
    return list(undefined)

if __name__ == "__main__":
    asyncio.run(test_edge_cases())
