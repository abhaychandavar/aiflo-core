NODES_GROUP_LAYOUT = {
    "input": {
        "name": "Inputs",
        "nodes": [
            { 
                "id": 'start', 
                "label": 'Input', 
                "type": 'start'
            },
            { 
                "id": 'text', 
                "label": 'Text', 
                "type": 'text',
                "parent": "start"
            },
            { 
                "id": 'image', 
                "label": 'Image', 
                "type": 'image',
                "parent": "start"
            }
        ]
    },
    "output": {
        "name": "Outputs",
        "nodes": [
            { 
                "id": 'res', 
                "label": 'Output', 
                "type": 'res'
            },
            { 
                "id": 'textOutput', 
                "label": 'Text output', 
                "type": 'textOutput',
                "parent": "res"
            },
            { 
                "id": 'imageOutput', 
                "label": 'Image output', 
                "type": 'imageOutput',
                "parent": "res"
            }
        ]
    },
    "dev": {
        "name": "Developer",
        "nodes": [
            { 
                "id": 'api-request', 
                "label": 'API Request', 
                "type": 'api-request'
            }
        ]
    },
    "llm": {
        "name": "LLMs",
        "nodes": [
            { 
                "id": 'llm', 
                "label": 'llm', 
                "type": 'llm' 
            }
        ]
    },
    "knowledgeBase": {
        "name": "Knowledge base",
        "nodes": [
            { 
                "id": 'knowledge-base', 
                "label": 'Knowledge base', 
                "type": 'knowledgeBase'
            }
        ]
    }
}

__all__=[NODES_GROUP_LAYOUT]