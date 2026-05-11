from fastapi import APIRouter, Query, HTTPException
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional

router = APIRouter()

@router.get("/cp/{cp}", tags=["Geo"])
async def get_cp_details(cp: str):
    """Get details for a specific Postal Code"""
    manager = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
    results = manager.search(cp) # Note: search in scd2_manager is hardcoded to LIMIT 10, I should probably improve it
    if not results:
        raise HTTPException(status_code=404, detail="CP not found")
    return results

@router.get("/search", tags=["Geo"])
async def search_geo(q: str = Query(..., min_length=3)):
    """Search for settlements, cities or states"""
    # General search across multiple tables (simplified for now)
    manager = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
    return manager.search(q)

@router.get("/states", tags=["Geo"])
async def get_states(q: Optional[str] = None):
    """List or search States"""
    manager = SCD2Manager(target_table="estados", natural_key="state_code", schema="geo")
    return manager.search(search_term=q, limit=50)

@router.get("/settlements", tags=["Geo"])
async def search_settlements(q: str = Query(..., min_length=3)):
    """Search Settlements (Colonias) by name"""
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    # For settlements, we use 'name' as the search field in the manager
    # I'll update the manager to support searching by 'name' if search_term is provided
    return manager.search(search_term=q, limit=50)
