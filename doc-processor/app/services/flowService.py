import aiohttp
from app.config.default import Settings

async def get_flow_by_id(flow_id: str):
    return {}

async def get_node_by_id(flow_id: str, node_id: str):
    url = f"{Settings.FLOW_SERVICE_BASE_URL}/api/v1/internal/flows/{flow_id}/nodes/{node_id}"
    headers = {
        'Authorization': f"Bearer {Settings.INTERNAL_SECRET_KEY}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data