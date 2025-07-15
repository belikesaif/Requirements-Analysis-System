"""
Code Generation Service for converting PlantUML Class Diagrams to Java code templates
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CodeGenerationService:
    """
    Service for generating skeletal Java code from PlantUML class diagrams
    """
    
    def __init__(self):
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
            'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
            'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
            'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'null',
            'package', 'private', 'protected', 'public', 'return', 'short', 'static',
            'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'try', 'void', 'volatile', 'while'
        }
    
    def generate_java_code(self, plantuml_code: str) -> Dict[str, Any]:
        """
        Main method to generate Java code from PlantUML class diagram
        """
        try:
            # Parse PlantUML code
            parsed_classes = self._parse_plantuml_classes(plantuml_code)
            
            # Generate Java files
            java_files = {}
            for class_name, class_info in parsed_classes.items():
                java_code = self._generate_java_class(class_name, class_info)
                java_files[f"{class_name}.java"] = java_code
            
            # Generate package structure suggestion
            package_structure = self._suggest_package_structure(parsed_classes)
            
            return {
                "success": True,
                "java_files": java_files,
                "package_structure": package_structure,
                "classes_generated": len(java_files),
                "generation_summary": self._generate_summary(parsed_classes)
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "java_files": {},
                "package_structure": {}
            }
    
    def _parse_plantuml_classes(self, plantuml_code: str) -> Dict[str, Dict]:
        """
        Parse PlantUML code to extract class information
        """
        classes = {}
        current_class = None
        
        lines = plantuml_code.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("'") or line.startswith("@"):
                continue
            
            # Class declaration
            class_match = re.match(r'class\s+(\w+)(?:\s+\{)?', line)
            if class_match:
                current_class = class_match.group(1)
                classes[current_class] = {
                    'attributes': [],
                    'methods': [],
                    'type': 'class',
                    'modifiers': self._extract_modifiers(line),
                    'extends': None,
                    'implements': []
                }
                continue
            
            # Interface declaration
            interface_match = re.match(r'interface\s+(\w+)(?:\s+\{)?', line)
            if interface_match:
                current_class = interface_match.group(1)
                classes[current_class] = {
                    'attributes': [],
                    'methods': [],
                    'type': 'interface',
                    'modifiers': [],
                    'extends': None,
                    'implements': []
                }
                continue
            
            # Abstract class
            if 'abstract class' in line:
                abstract_match = re.match(r'abstract\s+class\s+(\w+)(?:\s+\{)?', line)
                if abstract_match:
                    current_class = abstract_match.group(1)
                    classes[current_class] = {
                        'attributes': [],
                        'methods': [],
                        'type': 'abstract_class',
                        'modifiers': ['abstract'],
                        'extends': None,
                        'implements': []
                    }
                continue
            
            # Inheritance relationships
            if '-->' in line or '--|>' in line or '<|--' in line:
                self._parse_inheritance(line, classes)
                continue
            
            # Attributes and methods within class body
            if current_class and current_class in classes:
                if self._is_attribute(line):
                    attribute = self._parse_attribute(line)
                    if attribute:
                        classes[current_class]['attributes'].append(attribute)
                elif self._is_method(line):
                    method = self._parse_method(line)
                    if method:
                        classes[current_class]['methods'].append(method)
            
            # End of class
            if line == '}':
                current_class = None
        
        return classes
    
    def _extract_modifiers(self, line: str) -> List[str]:
        """Extract modifiers from class declaration"""
        modifiers = []
        if 'public' in line:
            modifiers.append('public')
        if 'private' in line:
            modifiers.append('private')
        if 'protected' in line:
            modifiers.append('protected')
        if 'abstract' in line:
            modifiers.append('abstract')
        if 'final' in line:
            modifiers.append('final')
        return modifiers
    
    def _parse_inheritance(self, line: str, classes: Dict):
        """Parse inheritance relationships"""
        # Simple inheritance parsing
        if '--|>' in line:
            parts = line.split('--|>')
            if len(parts) == 2:
                child = parts[0].strip()
                parent = parts[1].strip()
                if child in classes:
                    classes[child]['extends'] = parent
        elif '<|--' in line:
            parts = line.split('<|--')
            if len(parts) == 2:
                parent = parts[0].strip()
                child = parts[1].strip()
                if child in classes:
                    classes[child]['extends'] = parent
    
    def _is_attribute(self, line: str) -> bool:
        """Check if line represents an attribute"""
        # Simple heuristic: starts with visibility modifier and doesn't contain ()
        return (line.startswith(('+', '-', '#', '~')) or 
                re.match(r'\s*\w+\s+\w+', line)) and '(' not in line
    
    def _is_method(self, line: str) -> bool:
        """Check if line represents a method"""
        return '(' in line and ')' in line
    
    def _parse_attribute(self, line: str) -> Optional[Dict]:
        """Parse attribute from PlantUML line"""
        try:
            # Remove visibility symbols
            clean_line = line.replace('+', '').replace('-', '').replace('#', '').replace('~', '').strip()
            
            # Pattern: type name or name : type
            if ':' in clean_line:
                parts = clean_line.split(':')
                name = parts[0].strip()
                data_type = parts[1].strip() if len(parts) > 1 else 'String'
            else:
                # Pattern: type name
                parts = clean_line.split()
                if len(parts) >= 2:
                    data_type = parts[0]
                    name = parts[1]
                elif len(parts) == 1:
                    name = parts[0]
                    data_type = 'String'
                else:
                    return None
            
            visibility = self._get_visibility(line)
            
            return {
                'name': self._sanitize_name(name),
                'type': self._map_to_java_type(data_type),
                'visibility': visibility
            }
        except:
            return None
    
    def _parse_method(self, line: str) -> Optional[Dict]:
        """Parse method from PlantUML line"""
        try:
            # Remove visibility symbols
            clean_line = line.replace('+', '').replace('-', '').replace('#', '').replace('~', '').strip()
            
            # Extract method name and parameters
            if '(' in clean_line and ')' in clean_line:
                method_part = clean_line.split('(')[0].strip()
                params_part = clean_line[clean_line.find('(')+1:clean_line.rfind(')')].strip()
                
                # Parse return type and method name
                if ':' in method_part:
                    name_part, return_type = method_part.split(':', 1)
                    method_name = name_part.strip()
                    return_type = return_type.strip()
                else:
                    method_name = method_part
                    return_type = 'void'
                
                # Parse parameters
                parameters = []
                if params_part:
                    param_list = params_part.split(',')
                    for param in param_list:
                        param = param.strip()
                        if ':' in param:
                            param_name, param_type = param.split(':', 1)
                            parameters.append({
                                'name': self._sanitize_name(param_name.strip()),
                                'type': self._map_to_java_type(param_type.strip())
                            })
                        else:
                            parameters.append({
                                'name': self._sanitize_name(param),
                                'type': 'String'
                            })
                
                visibility = self._get_visibility(line)
                
                return {
                    'name': self._sanitize_name(method_name),
                    'return_type': self._map_to_java_type(return_type),
                    'parameters': parameters,
                    'visibility': visibility
                }
        except:
            return None
        
        return None
    
    def _get_visibility(self, line: str) -> str:
        """Extract visibility from PlantUML line"""
        if line.startswith('+'):
            return 'public'
        elif line.startswith('-'):
            return 'private'
        elif line.startswith('#'):
            return 'protected'
        elif line.startswith('~'):
            return 'package'
        else:
            return 'public'  # default
    
    def _map_to_java_type(self, plantuml_type: str) -> str:
        """Map PlantUML types to Java types"""
        type_mapping = {
            'string': 'String',
            'String': 'String',
            'int': 'int',
            'integer': 'int',
            'Integer': 'Integer',
            'boolean': 'boolean',
            'Boolean': 'Boolean',
            'double': 'double',
            'Double': 'Double',
            'float': 'float',
            'Float': 'Float',
            'long': 'long',
            'Long': 'Long',
            'char': 'char',
            'Character': 'Character',
            'byte': 'byte',
            'Byte': 'Byte',
            'short': 'short',
            'Short': 'Short',
            'Date': 'Date',
            'LocalDate': 'LocalDate',
            'LocalDateTime': 'LocalDateTime',
            'List': 'List',
            'ArrayList': 'ArrayList',
            'Set': 'Set',
            'Map': 'Map',
            'void': 'void'
        }
        
        # Handle arrays
        if plantuml_type.endswith('[]'):
            base_type = plantuml_type[:-2]
            mapped_base = type_mapping.get(base_type, base_type)
            return f"{mapped_base}[]"
        
        # Handle generic types
        if '<' in plantuml_type and '>' in plantuml_type:
            return plantuml_type  # Keep as is for generics
        
        return type_mapping.get(plantuml_type, plantuml_type)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name to be valid Java identifier"""
        # Remove special characters and spaces
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = '_' + name
        
        # Check against Java keywords
        if name.lower() in self.java_keywords:
            name = name + '_'
        
        return name if name else 'unnamed'
    
    def _generate_java_class(self, class_name: str, class_info: Dict) -> str:
        """Generate Java code for a class"""
        lines = []
        
        # Package declaration (placeholder)
        lines.append("package com.generated.model;")
        lines.append("")
        
        # Imports
        imports = self._generate_imports(class_info)
        for imp in imports:
            lines.append(f"import {imp};")
        if imports:
            lines.append("")
        
        # Class declaration
        class_declaration = self._generate_class_declaration(class_name, class_info)
        lines.append(class_declaration)
        lines.append("{")
        
        # Attributes
        if class_info['attributes']:
            lines.append("")
            lines.append("    // Attributes")
            for attr in class_info['attributes']:
                attr_line = f"    {attr['visibility']} {attr['type']} {attr['name']};"
                lines.append(attr_line)
        
        # Default constructor
        lines.append("")
        lines.append("    // Default constructor")
        lines.append(f"    public {class_name}() {{")
        lines.append("        // TODO: Initialize default values")
        lines.append("    }")
        
        # Parameterized constructor (if attributes exist)
        if class_info['attributes']:
            lines.append("")
            lines.append("    // Parameterized constructor")
            params = ", ".join([f"{attr['type']} {attr['name']}" for attr in class_info['attributes']])
            lines.append(f"    public {class_name}({params}) {{")
            for attr in class_info['attributes']:
                lines.append(f"        this.{attr['name']} = {attr['name']};")
            lines.append("    }")
        
        # Getters and Setters
        if class_info['attributes']:
            lines.append("")
            lines.append("    // Getters and Setters")
            for attr in class_info['attributes']:
                # Getter
                getter_name = f"get{attr['name'].capitalize()}"
                lines.append(f"    public {attr['type']} {getter_name}() {{")
                lines.append(f"        return {attr['name']};")
                lines.append("    }")
                lines.append("")
                
                # Setter
                setter_name = f"set{attr['name'].capitalize()}"
                lines.append(f"    public void {setter_name}({attr['type']} {attr['name']}) {{")
                lines.append(f"        this.{attr['name']} = {attr['name']};")
                lines.append("    }")
                lines.append("")
        
        # Methods
        if class_info['methods']:
            lines.append("    // Methods")
            for method in class_info['methods']:
                method_line = self._generate_method_signature(method)
                lines.append(f"    {method_line} {{")
                
                if method['return_type'] != 'void':
                    default_return = self._get_default_return_value(method['return_type'])
                    lines.append(f"        // TODO: Implement method logic")
                    lines.append(f"        return {default_return};")
                else:
                    lines.append("        // TODO: Implement method logic")
                
                lines.append("    }")
                lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_imports(self, class_info: Dict) -> List[str]:
        """Generate import statements"""
        imports = set()
        
        # Check attributes for import needs
        for attr in class_info['attributes']:
            if attr['type'] in ['Date']:
                imports.add('java.util.Date')
            elif attr['type'] in ['LocalDate']:
                imports.add('java.time.LocalDate')
            elif attr['type'] in ['LocalDateTime']:
                imports.add('java.time.LocalDateTime')
            elif attr['type'] in ['List', 'ArrayList']:
                imports.add('java.util.List')
                imports.add('java.util.ArrayList')
            elif attr['type'] in ['Set']:
                imports.add('java.util.Set')
            elif attr['type'] in ['Map']:
                imports.add('java.util.Map')
        
        # Check methods for import needs
        for method in class_info['methods']:
            if method['return_type'] in ['Date']:
                imports.add('java.util.Date')
            elif method['return_type'] in ['LocalDate']:
                imports.add('java.time.LocalDate')
            elif method['return_type'] in ['LocalDateTime']:
                imports.add('java.time.LocalDateTime')
            elif method['return_type'] in ['List', 'ArrayList']:
                imports.add('java.util.List')
                imports.add('java.util.ArrayList')
        
        return sorted(list(imports))
    
    def _generate_class_declaration(self, class_name: str, class_info: Dict) -> str:
        """Generate class declaration line"""
        modifiers = []
        
        if 'public' not in class_info.get('modifiers', []):
            modifiers.append('public')
        
        modifiers.extend(class_info.get('modifiers', []))
        
        if class_info['type'] == 'interface':
            declaration = f"{' '.join(modifiers)} interface {class_name}"
        elif class_info['type'] == 'abstract_class':
            declaration = f"{' '.join(modifiers)} class {class_name}"
        else:
            declaration = f"{' '.join(modifiers)} class {class_name}"
        
        if class_info.get('extends'):
            declaration += f" extends {class_info['extends']}"
        
        if class_info.get('implements'):
            interfaces = ', '.join(class_info['implements'])
            declaration += f" implements {interfaces}"
        
        return declaration
    
    def _generate_method_signature(self, method: Dict) -> str:
        """Generate method signature"""
        params = ", ".join([f"{param['type']} {param['name']}" for param in method['parameters']])
        return f"{method['visibility']} {method['return_type']} {method['name']}({params})"
    
    def _get_default_return_value(self, return_type: str) -> str:
        """Get default return value for method"""
        defaults = {
            'int': '0',
            'long': '0L',
            'double': '0.0',
            'float': '0.0f',
            'boolean': 'false',
            'char': "'\0'",
            'byte': '0',
            'short': '0'
        }
        
        if return_type in defaults:
            return defaults[return_type]
        else:
            return 'null'
    
    def _suggest_package_structure(self, classes: Dict) -> Dict[str, List[str]]:
        """Suggest package structure based on class names and types"""
        packages = {
            'com.generated.model': [],
            'com.generated.service': [],
            'com.generated.controller': [],
            'com.generated.util': []
        }
        
        for class_name, class_info in classes.items():
            name_lower = class_name.lower()
            
            if any(keyword in name_lower for keyword in ['service', 'manager', 'handler']):
                packages['com.generated.service'].append(class_name)
            elif any(keyword in name_lower for keyword in ['controller', 'rest', 'api']):
                packages['com.generated.controller'].append(class_name)
            elif any(keyword in name_lower for keyword in ['util', 'helper', 'tool']):
                packages['com.generated.util'].append(class_name)
            else:
                packages['com.generated.model'].append(class_name)
        
        # Remove empty packages
        return {k: v for k, v in packages.items() if v}
    
    def _generate_summary(self, classes: Dict) -> Dict[str, Any]:
        """Generate summary of generated code"""
        total_classes = len(classes)
        total_attributes = sum(len(c['attributes']) for c in classes.values())
        total_methods = sum(len(c['methods']) for c in classes.values())
        
        class_types = {}
        for class_info in classes.values():
            class_type = class_info['type']
            class_types[class_type] = class_types.get(class_type, 0) + 1
        
        return {
            'total_classes': total_classes,
            'total_attributes': total_attributes,
            'total_methods': total_methods,
            'class_types': class_types,
            'estimated_lines_of_code': self._estimate_lines_of_code(classes)
        }
    
    def _estimate_lines_of_code(self, classes: Dict) -> int:
        """Estimate total lines of code generated"""
        base_lines_per_class = 15  # Package, imports, class declaration, constructors, closing brace
        lines_per_attribute = 8    # Getter and setter
        lines_per_method = 5       # Method signature and basic body
        
        total_lines = 0
        for class_info in classes.values():
            total_lines += base_lines_per_class
            total_lines += len(class_info['attributes']) * lines_per_attribute
            total_lines += len(class_info['methods']) * lines_per_method
        
        return total_lines
