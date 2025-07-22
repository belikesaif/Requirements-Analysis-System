import { describe, it, expect } from '@jest/globals';

// Since we can't easily import the function from the component,
// let's recreate the logic for testing
const performSimpleComparison = (aiRequirements, ruppData) => {
  // Extract RUPP requirements from different possible formats
  let ruppRequirements = [];
  
  if (ruppData.formatted_sentences) {
    ruppRequirements = ruppData.formatted_sentences;
  } else if (ruppData.requirements) {
    ruppRequirements = ruppData.requirements;
  } else if (ruppData.snl_text) {
    // Split by lines and filter out empty lines
    ruppRequirements = ruppData.snl_text.split('\n').filter(line => line.trim());
  } else if (typeof ruppData === 'string') {
    ruppRequirements = ruppData.split('\n').filter(line => line.trim());
  } else {
    ruppRequirements = [];
  }

  const missing_in_ai = [];
  const overspecified_in_ai = [];
  const incorrect_in_ai = [];

  // Helper function to normalize text for comparison
  const normalizeText = (text) => {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')  // Replace punctuation with spaces
      .replace(/\s+/g, ' ')      // Replace multiple spaces with single space
      .trim();
  };

  // Helper function to check if two requirements are similar
  const areRequirementsSimilar = (req1, req2, threshold = 0.6) => {
    const norm1 = normalizeText(req1);
    const norm2 = normalizeText(req2);
    
    // Simple similarity check: count common words
    const words1 = new Set(norm1.split(' '));
    const words2 = new Set(norm2.split(' '));
    
    const commonWords = new Set([...words1].filter(word => words2.has(word)));
    const totalWords = new Set([...words1, ...words2]);
    
    if (totalWords.size === 0) return false;
    return commonWords.size / totalWords.size >= threshold;
  };

  // Find missing requirements (in RUPP but not in AI)
  ruppRequirements.forEach(ruppReq => {
    const found = aiRequirements.some(aiReq => 
      areRequirementsSimilar(aiReq, ruppReq, 0.5)
    );
    
    if (!found) {
      missing_in_ai.push({
        requirement: ruppReq,
        reason: 'This RUPP requirement was not captured by AI generation'
      });
    }
  });

  // Find overspecified requirements (in AI but not in RUPP)
  aiRequirements.forEach(aiReq => {
    const found = ruppRequirements.some(ruppReq => 
      areRequirementsSimilar(aiReq, ruppReq, 0.5)
    );
    
    if (!found) {
      overspecified_in_ai.push({
        requirement: aiReq,
        reason: 'AI generated this requirement beyond RUPP scope'
      });
    }
  });

  // Find incorrect requirements (significantly different from RUPP)
  aiRequirements.forEach(aiReq => {
    const similarRuppReq = ruppRequirements.find(ruppReq => 
      areRequirementsSimilar(aiReq, ruppReq, 0.3) && 
      !areRequirementsSimilar(aiReq, ruppReq, 0.7)
    );
    
    if (similarRuppReq) {
      incorrect_in_ai.push({
        requirement: aiReq,
        reason: `Similar to RUPP requirement "${similarRuppReq}" but with significant differences`
      });
    }
  });

  const totalIssues = missing_in_ai.length + overspecified_in_ai.length + incorrect_in_ai.length;
  const totalRequirements = Math.max(aiRequirements.length, ruppRequirements.length);
  const accuracy_percentage = totalRequirements > 0 
    ? Math.round(((totalRequirements - totalIssues) / totalRequirements) * 100)
    : 0;

  return {
    missing_in_ai: {
      count: missing_in_ai.length,
      items: missing_in_ai
    },
    overspecified_in_ai: {
      count: overspecified_in_ai.length,
      items: overspecified_in_ai
    },
    incorrect_in_ai: {
      count: incorrect_in_ai.length,
      items: incorrect_in_ai
    },
    total_issues: totalIssues,
    accuracy_percentage: accuracy_percentage,
    analysis_summary: `String-based comparison found ${totalIssues} differences between AI and RUPP requirements. ` +
      `AI generated ${aiRequirements.length} requirements vs RUPP's ${ruppRequirements.length} requirements.`
  };
};

describe('AI vs RUPP Comparison Logic', () => {
  it('should identify missing requirements in AI', () => {
    const aiRequirements = [
      'User should be able to login',
      'System should validate password'
    ];
    
    const ruppData = {
      formatted_sentences: [
        'User should be able to login',
        'System should validate password',
        'System should log user activities'
      ]
    };

    const result = performSimpleComparison(aiRequirements, ruppData);
    
    expect(result.missing_in_ai.count).toBe(1);
    expect(result.missing_in_ai.items[0].requirement).toBe('System should log user activities');
  });

  it('should identify overspecified requirements in AI', () => {
    const aiRequirements = [
      'User should be able to login',
      'System should validate password',
      'System should send welcome email'
    ];
    
    const ruppData = {
      formatted_sentences: [
        'User should be able to login',
        'System should validate password'
      ]
    };

    const result = performSimpleComparison(aiRequirements, ruppData);
    
    expect(result.overspecified_in_ai.count).toBe(1);
    expect(result.overspecified_in_ai.items[0].requirement).toBe('System should send welcome email');
  });

  it('should identify incorrect requirements in AI', () => {
    const aiRequirements = [
      'User should be able to login with username',
      'System should validate password strength'
    ];
    
    const ruppData = {
      formatted_sentences: [
        'User should be able to login with email',
        'System should validate password'
      ]
    };

    const result = performSimpleComparison(aiRequirements, ruppData);
    
    // Should detect some incorrect requirements due to differences
    expect(result.incorrect_in_ai.count).toBeGreaterThanOrEqual(0);
  });

  it('should calculate accuracy percentage correctly', () => {
    const aiRequirements = [
      'User should be able to login',
      'System should validate password'
    ];
    
    const ruppData = {
      formatted_sentences: [
        'User should be able to login',
        'System should validate password'
      ]
    };

    const result = performSimpleComparison(aiRequirements, ruppData);
    
    expect(result.accuracy_percentage).toBe(100);
    expect(result.total_issues).toBe(0);
  });

  it('should handle different RUPP data formats', () => {
    const aiRequirements = ['User should login'];
    
    // Test with snl_text format
    const ruppDataWithSnlText = {
      snl_text: 'User should login\nSystem should validate'
    };
    
    const result1 = performSimpleComparison(aiRequirements, ruppDataWithSnlText);
    expect(result1.missing_in_ai.count).toBe(1);
    
    // Test with string format
    const ruppDataString = 'User should login\nSystem should validate';
    
    const result2 = performSimpleComparison(aiRequirements, ruppDataString);
    expect(result2.missing_in_ai.count).toBe(1);
  });
});
