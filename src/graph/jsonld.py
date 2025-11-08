"""
JSON-LD context and serialization utilities for VTA.
Enables structured data representation with semantic meaning.
"""
import json
from typing import Dict, Any, List
from pathlib import Path


def get_jsonld_context() -> Dict[str, Any]:
    """
    Get JSON-LD context for VTA ontology.
    
    Returns:
        JSON-LD context dictionary
    """
    return {
        "@context": {
            "@vocab": "http://nissan-ntce.cranfield.ac.uk/vta/ontology#",
            "vta": "http://nissan-ntce.cranfield.ac.uk/vta/ontology#",
            "vtad": "http://nissan-ntce.cranfield.ac.uk/vta/data#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "dcterms": "http://purl.org/dc/terms/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            
            # Classes
            "Vehicle": "vta:Vehicle",
            "Platform": "vta:Platform",
            "Component": "vta:Component",
            "VehicleSystem": "vta:VehicleSystem",
            "TestScenario": "vta:TestScenario",
            "RegulatoryStandard": "vta:RegulatoryStandard",
            "TestType": "vta:TestType",
            "Facility": "vta:Facility",
            
            # Properties
            "id": "@id",
            "type": "@type",
            "label": "rdfs:label",
            "description": "dcterms:description",
            
            # Object properties
            "onPlatform": {
                "@id": "vta:onPlatform",
                "@type": "@id"
            },
            "hasComponent": {
                "@id": "vta:hasComponent",
                "@type": "@id"
            },
            "belongsToSystem": {
                "@id": "vta:belongsToSystem",
                "@type": "@id"
            },
            "requiresTest": {
                "@id": "vta:requiresTest",
                "@type": "@id"
            },
            "testsComponent": {
                "@id": "vta:testsComponent",
                "@type": "@id"
            },
            "followsStandard": {
                "@id": "vta:followsStandard",
                "@type": "@id"
            },
            "isType": {
                "@id": "vta:isType",
                "@type": "@id"
            },
            
            # Data properties
            "modelId": "vta:modelId",
            "testType": "vta:testType",
            "complexityScore": {
                "@id": "vta:complexityScore",
                "@type": "xsd:integer"
            },
            "riskLevel": "vta:riskLevel",
            "estimatedDuration": {
                "@id": "vta:estimatedDuration",
                "@type": "xsd:float"
            },
            "estimatedCost": {
                "@id": "vta:estimatedCost",
                "@type": "xsd:float"
            },
            "certificationRequired": {
                "@id": "vta:certificationRequired",
                "@type": "xsd:boolean"
            },
            "criticality": "vta:criticality",
            "category": "vta:category",
        }
    }


def serialize_vehicle_jsonld(vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize vehicle data to JSON-LD format.
    
    Args:
        vehicle_data: Vehicle data dictionary
        
    Returns:
        JSON-LD representation
    """
    context = get_jsonld_context()
    
    return {
        **context,
        "@graph": [
            {
                "@id": f"vtad:vehicle/{vehicle_data.get('model_id', 'unknown')}",
                "@type": "Vehicle",
                "label": vehicle_data.get("name"),
                "modelId": vehicle_data.get("model_id"),
                "onPlatform": f"vtad:platform/{vehicle_data.get('platform')}" if vehicle_data.get('platform') else None,
            }
        ]
    }


def serialize_component_jsonld(component_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize component data to JSON-LD format.
    
    Args:
        component_data: Component data dictionary
        
    Returns:
        JSON-LD representation
    """
    context = get_jsonld_context()
    
    return {
        **context,
        "@graph": [
            {
                "@id": f"vtad:component/{component_data.get('component_id', 'unknown')}",
                "@type": "Component",
                "label": component_data.get("name"),
                "criticality": component_data.get("criticality"),
                "belongsToSystem": f"vtad:system/{component_data.get('system')}" if component_data.get('system') else None,
            }
        ]
    }


def serialize_test_scenario_jsonld(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize test scenario data to JSON-LD format.
    
    Args:
        scenario_data: Test scenario data dictionary
        
    Returns:
        JSON-LD representation
    """
    context = get_jsonld_context()
    
    return {
        **context,
        "@graph": [
            {
                "@id": f"vtad:scenario/{scenario_data.get('scenario_id', 'unknown')}",
                "@type": "TestScenario",
                "label": scenario_data.get("test_name"),
                "testType": scenario_data.get("test_type"),
                "description": scenario_data.get("description"),
                "complexityScore": scenario_data.get("complexity_score"),
                "riskLevel": scenario_data.get("risk_level"),
                "estimatedDuration": scenario_data.get("estimated_duration_hours"),
                "estimatedCost": scenario_data.get("estimated_cost_gbp"),
                "certificationRequired": scenario_data.get("certification_required"),
            }
        ]
    }


def serialize_multiple_jsonld(items: List[Dict[str, Any]], item_type: str) -> Dict[str, Any]:
    """
    Serialize multiple items to JSON-LD format.
    
    Args:
        items: List of item dictionaries
        item_type: Type of items ("vehicle", "component", "scenario")
        
    Returns:
        JSON-LD representation with multiple items in @graph
    """
    context = get_jsonld_context()
    graph = []
    
    for item in items:
        if item_type == "vehicle":
            graph.append({
                "@id": f"vtad:vehicle/{item.get('model_id', 'unknown')}",
                "@type": "Vehicle",
                "label": item.get("name"),
                "modelId": item.get("model_id"),
                "onPlatform": f"vtad:platform/{item.get('platform')}" if item.get('platform') else None,
            })
        elif item_type == "component":
            graph.append({
                "@id": f"vtad:component/{item.get('component_id', 'unknown')}",
                "@type": "Component",
                "label": item.get("name"),
                "criticality": item.get("criticality"),
            })
        elif item_type == "scenario":
            graph.append({
                "@id": f"vtad:scenario/{item.get('scenario_id', 'unknown')}",
                "@type": "TestScenario",
                "label": item.get("test_name"),
                "testType": item.get("test_type"),
                "complexityScore": item.get("complexity_score"),
                "riskLevel": item.get("risk_level"),
            })
    
    return {
        **context,
        "@graph": graph
    }


def save_jsonld(data: Dict[str, Any], output_path: str) -> None:
    """
    Save JSON-LD data to file.
    
    Args:
        data: JSON-LD data
        output_path: Output file path
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_jsonld(input_path: str) -> Dict[str, Any]:
    """
    Load JSON-LD data from file.
    
    Args:
        input_path: Input file path
        
    Returns:
        JSON-LD data dictionary
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compact_jsonld(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compact JSON-LD data using VTA context.
    
    Args:
        data: JSON-LD data
        
    Returns:
        Compacted JSON-LD
    """
    # In a full implementation, would use pyld library
    # For now, just ensure context is present
    context = get_jsonld_context()
    if "@context" not in data:
        data = {**context, **data}
    return data


def expand_jsonld(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Expand JSON-LD data to remove context.
    
    Args:
        data: JSON-LD data
        
    Returns:
        Expanded JSON-LD (list of node objects)
    """
    # In a full implementation, would use pyld library
    # For now, return @graph or wrap in list
    if "@graph" in data:
        return data["@graph"]
    else:
        return [data]


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("JSON-LD SERIALIZATION TEST")
    print("=" * 70)
    
    # Test vehicle serialization
    print("\n[1/4] Vehicle JSON-LD:")
    vehicle = {
        "model_id": "Ariya",
        "name": "Ariya",
        "platform": "EV"
    }
    vehicle_jsonld = serialize_vehicle_jsonld(vehicle)
    print(json.dumps(vehicle_jsonld, indent=2)[:500] + "...")
    
    # Test component serialization
    print("\n[2/4] Component JSON-LD:")
    component = {
        "component_id": "High_Voltage_Battery",
        "name": "High Voltage Battery",
        "criticality": "critical",
        "system": "Battery"
    }
    component_jsonld = serialize_component_jsonld(component)
    print(json.dumps(component_jsonld, indent=2)[:500] + "...")
    
    # Test scenario serialization
    print("\n[3/4] Test Scenario JSON-LD:")
    scenario = {
        "scenario_id": "SCN-001",
        "test_name": "Battery Thermal Test",
        "test_type": "performance",
        "description": "Thermal management validation",
        "complexity_score": 7,
        "risk_level": "high",
        "estimated_duration_hours": 48.5,
        "estimated_cost_gbp": 12000.0,
        "certification_required": True
    }
    scenario_jsonld = serialize_test_scenario_jsonld(scenario)
    print(json.dumps(scenario_jsonld, indent=2)[:600] + "...")
    
    # Test context
    print("\n[4/4] VTA Context:")
    context = get_jsonld_context()
    print(f"Context has {len(context['@context'])} entries")
    print("Sample entries:")
    for key in list(context['@context'].keys())[:5]:
        print(f"  {key}: {context['@context'][key]}")
    
    print("\n[OK] JSON-LD serialization test complete")

