from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager
from typing import List

from models import (
    CharacterData, EnemyData, BuffData, Skill, Rotation,
    CalculationRequest, CalculationResponse, SkillResult, CalculationStep
)
from calculator import (
    calculate_final_attack_with_steps, calculate_skill_damage
)
from api_client import (
    fetch_character_list, fetch_weapon_list,
    fetch_character_detail, fetch_weapon_detail,
    character_list_cache, weapon_list_cache
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global character_list_cache, weapon_list_cache
    print("正在初始化数据...")
    character_list_cache = fetch_character_list()
    weapon_list_cache = fetch_weapon_list()
    print(f"初始化完成，角色: {len(character_list_cache)}, 武器: {len(weapon_list_cache)}")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_index():
    return FileResponse("index.html")


@app.get("/api/characters")
async def get_characters():
    return {"success": True, "characters": character_list_cache}


@app.get("/api/weapons")
async def get_weapons(weapon_type: str | None = None):
    if weapon_type is not None and weapon_type.strip() != '':
        try:
            weapon_type_int = int(weapon_type)
            filtered_weapons = [w for w in weapon_list_cache if w.get('weaponType') == weapon_type_int]
            return {"success": True, "weapons": filtered_weapons}
        except ValueError:
            pass
    return {"success": True, "weapons": weapon_list_cache}


@app.get("/api/character/{character_id}")
async def get_character_detail(character_id: str):
    detail = fetch_character_detail(character_id)
    if detail:
        return {"success": True, "data": {"baseAtk": detail.get('baseAtk')}}
    return {"success": False, "error": "获取角色详情失败"}


@app.get("/api/weapon/{weapon_id}")
async def get_weapon_detail(weapon_id: str):
    detail = fetch_weapon_detail(weapon_id)
    if detail:
        return {
            "success": True, 
            "data": {
                "baseAtk": detail.get('baseAtk'),
                "substatType": detail.get('substatType'),
                "substatValue": detail.get('substatValue')
            }
        }
    return {"success": False, "error": "获取武器详情失败"}


@app.post("/api/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    try:
        char_data = request.charData
        enemy_data = request.enemyData
        buff_data = request.buffData
        skills_list = request.skills
        rotations = request.rotations
        
        final_attack, _ = calculate_final_attack_with_steps(char_data, buff_data)
        total_damage = 0
        skill_results = []
        all_steps: List[CalculationStep] = []
        
        for rotation in rotations:
            skill_id = rotation.skillId
            count = rotation.count
            if count > 0:
                skill = next((s for s in skills_list if s.id == skill_id), None)
                if skill:
                    steps: List[CalculationStep] = []
                    single_damage = calculate_skill_damage(skill, char_data, enemy_data, buff_data, steps)
                    total_skill_damage = single_damage * count
                    total_damage += total_skill_damage
                    skill_results.append(SkillResult(
                        skill=skill,
                        count=count,
                        singleDamage=single_damage,
                        totalSkillDamage=total_skill_damage
                    ))
                    all_steps.extend(steps)
        
        return CalculationResponse(
            success=True,
            finalAttack=final_attack,
            totalDamage=total_damage,
            skillResults=skill_results,
            calculationSteps=all_steps
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return CalculationResponse(
            success=False,
            error=str(e)
        )


@app.get("/favicon.ico")
async def favicon():
    return "", 204


app.mount("/", StaticFiles(directory="."), name="static")


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=port)
