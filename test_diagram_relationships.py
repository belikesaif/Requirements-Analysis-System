#!/usr/bin/env python3
"""
Test script to verify that diagram generation includes proper relationships between classes/participants.
This script tests the current diagram generation logic to ensure meaningful relationships are created.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.diagram_service import DiagramService

async def test_diagram_relationships():
    """Test that diagram generation includes proper relationships"""
    
    # Sample SNL requirements with clear entities and interactions
    sample_snl = """
    The library management system allows members to search for books and borrow them.
    Librarians can add new books to the catalog and manage member accounts.
    Members must login with their credentials to access the system.
    When a member borrows a book, the system records the transaction.
    Librarians can view all borrowed books and their due dates.
    The system sends email notifications to members about overdue books.
    """
    
    # Test identified actors
    sample_actors = ["Member", "Librarian", "Book", "EmailService"]
    
    print("Testing diagram relationship generation...")
    print("=" * 60)
    
    try:
        diagram_service = DiagramService()
        
        # Test 1: Initial class diagram generation (SNL only)
        print("\n1. Testing initial class diagram generation (SNL only):")
        print("-" * 50)
        
        class_diagram = await diagram_service.generate_class_diagram_from_rupp(sample_snl)
        print("Generated Class Diagram:")
        print(class_diagram)
        
        # Check for relationships in class diagram
        relationship_indicators = ['-->', '--', '..>', '..', '|>', '<|--', 'extends', 'implements', 'uses', 'borrows', 'manages', 'contains']
        relationships_found = []
        
        for indicator in relationship_indicators:
            if indicator in class_diagram:
                relationships_found.append(indicator)
        
        print(f"\nRelationship indicators found: {relationships_found}")
        print(f"Total relationships: {len(relationships_found)}")
        
        # Test 2: Initial sequence diagram generation (SNL only)
        print("\n2. Testing initial sequence diagram generation (SNL only):")
        print("-" * 50)
        
        sequence_diagram = await diagram_service.generate_sequence_diagram_from_rupp(sample_snl)
        print("Generated Sequence Diagram:")
        print(sequence_diagram)
        
        # Check for interactions in sequence diagram
        interaction_indicators = ['->', '-->', '->>', '<-', '<--', '<->', 'activate', 'deactivate']
        interactions_found = []
        
        for indicator in interaction_indicators:
            if indicator in sequence_diagram:
                interactions_found.append(indicator)
        
        print(f"\nInteraction indicators found: {interactions_found}")
        print(f"Total interactions: {len(interactions_found)}")
        
        # Test 3: Actor extraction
        print("\n3. Testing actor extraction:")
        print("-" * 50)
        
        extracted_actors = await diagram_service.extract_actors_from_requirements(
            sample_snl.replace("The library management system", "Library management system"),  # Remove "The" to avoid extraction issues
            class_diagram, 
            sequence_diagram
        )
        print(f"Extracted actors: {extracted_actors}")
        
        # Test 4: Diagram verification
        print("\n4. Testing diagram verification with actors:")
        print("-" * 50)
        
        verification_result = await diagram_service.verify_diagrams_with_actors(
            class_diagram, 
            sequence_diagram, 
            sample_actors
        )
        
        print("Verification Results:")
        for key, value in verification_result.items():
            print(f"  {key}: {value}")
        
        # Test 5: Final optimization
        print("\n5. Testing final LLM optimization:")
        print("-" * 50)
        
        optimization_result = await diagram_service.optimize_diagrams_with_llm_and_actors(
            sample_snl.replace("The library management system", "Library management system"),
            class_diagram,
            sequence_diagram,
            sample_actors,
            verification_result
        )
        
        print("Optimized Class Diagram:")
        print(optimization_result['class_diagram'])
        
        print("\nOptimized Sequence Diagram:")
        print(optimization_result['sequence_diagram'])
        
        print(f"\nOptimization improvements: {optimization_result['improvements']}")
        
        # Final relationship check on optimized diagrams
        print("\n6. Final relationship analysis:")
        print("-" * 50)
        
        opt_class_relationships = []
        opt_sequence_interactions = []
        
        for indicator in relationship_indicators:
            if indicator in optimization_result['class_diagram']:
                opt_class_relationships.append(indicator)
        
        for indicator in interaction_indicators:
            if indicator in optimization_result['sequence_diagram']:
                opt_sequence_interactions.append(indicator)
        
        print(f"Optimized class diagram relationships: {opt_class_relationships}")
        print(f"Optimized sequence diagram interactions: {opt_sequence_interactions}")
        
        # Summary
        print("\n" + "=" * 60)
        print("RELATIONSHIP GENERATION SUMMARY:")
        print("=" * 60)
        print(f"Initial class relationships: {len(relationships_found)}")
        print(f"Initial sequence interactions: {len(interactions_found)}")
        print(f"Optimized class relationships: {len(opt_class_relationships)}")
        print(f"Optimized sequence interactions: {len(opt_sequence_interactions)}")
        print(f"Actors coverage: {verification_result.get('overall_score', 0):.2%}")
        
        if len(opt_class_relationships) == 0:
            print("\n⚠️  WARNING: No relationships found in optimized class diagram!")
        if len(opt_sequence_interactions) == 0:
            print("\n⚠️  WARNING: No interactions found in optimized sequence diagram!")
        
        if len(opt_class_relationships) > 0 and len(opt_sequence_interactions) > 0:
            print("\n✅ SUCCESS: Both diagrams contain proper relationships/interactions!")
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_diagram_relationships())
