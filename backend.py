from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import requests
from contextlib import asynccontextmanager

character_list_cache = []
weapon_list_cache = []

def fetch_character_list():
    try:
        response = requests.get('https://api-v2.encore.moe/api/zh-Hans/character', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'roleList' in data:
                characters = []
                for item in data['roleList']:
                    weapon_type = item.get('WeaponType')
                    if isinstance(weapon_type, dict):
                        weapon_type = weapon_type.get('Id')
                    characters.append({
                        'id': item.get('Id'),
                        'name': item.get('Name'),
                        'weaponType': weapon_type
                    })
                return characters
    except Exception as e:
        print(f"获取角色列表失败: {e}")
    return []

def fetch_weapon_list():
    try:
        response = requests.get('https://api-v2.encore.moe/api/zh-Hans/weapon', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'weapons' in data:
                weapons = []
                for item in data['weapons']:
                    weapons.append({
                        'id': item.get('Id'),
                        'name': item.get('Name'),
                        'weaponType': item.get('Type') or item.get('WeaponType')
                    })
                return weapons
    except Exception as e:
        print(f"获取武器列表失败: {e}")
    return []

def find_base_atk_from_properties(data):
    if not isinstance(data, dict):
        return None
    
    if 'Properties' in data:
        properties = data['Properties']
        if isinstance(properties, list):
            for prop in properties:
                if isinstance(prop, dict):
                    if prop.get('Name') == '攻击':
                        if 'GrowthValues' in prop:
                            growth_values = prop['GrowthValues']
                            if isinstance(growth_values, list):
                                for gv in growth_values:
                                    if isinstance(gv, dict):
                                        level_val = gv.get('level') or gv.get('Level')
                                        if level_val == 90 or (isinstance(level_val, str) and level_val == '90'):
                                            value = gv.get('value') or gv.get('Value')
                                            if value is not None:
                                                if isinstance(value, str):
                                                    try:
                                                        return float(value)
                                                    except ValueError:
                                                        pass
                                                elif isinstance(value, (int, float)):
                                                    return value
    return None

def find_weapon_substat(data):
    if not isinstance(data, dict):
        return None, None
    
    if 'Properties' not in data:
        return None, None
    
    properties = data['Properties']
    if not isinstance(properties, list):
        return None, None
    
    for i, prop in enumerate(properties):
        if isinstance(prop, dict):
            prop_name = prop.get('Name')
            
            if i == 0:
                continue
            
            if prop_name:
                if 'GrowthValues' in prop:
                    growth_values = prop['GrowthValues']
                    if isinstance(growth_values, list):
                        for gv in growth_values:
                            if isinstance(gv, dict):
                                level_val = gv.get('level') or gv.get('Level')
                                value = gv.get('value') or gv.get('Value')
                                
                                if level_val == 90 or (isinstance(level_val, str) and level_val == '90'):
                                    if value is not None:
                                        final_value = value
                                        if isinstance(final_value, str):
                                            final_value = final_value.replace('%', '')
                                            try:
                                                final_value = float(final_value)
                                            except ValueError:
                                                pass
                                        return prop_name, final_value
    return None, None

def fetch_character_detail(character_id):
    try:
        response = requests.get(f'https://api-v2.encore.moe/api/zh-Hans/character/{character_id}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            base_atk = find_base_atk_from_properties(data)
            print(f"角色详情 - 找到90级攻击力: {base_atk}")
            result = {'raw': data}
            if base_atk is not None:
                result['baseAtk'] = base_atk
            return result
    except Exception as e:
        print(f"获取角色详情失败: {e}")
    return None

def fetch_weapon_detail(weapon_id):
    try:
        response = requests.get(f'https://api-v2.encore.moe/api/zh-Hans/weapon/{weapon_id}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            base_atk = find_base_atk_from_properties(data)
            substat_type, substat_value = find_weapon_substat(data)
            result = {'raw': data}
            if base_atk is not None:
                result['baseAtk'] = base_atk
            if substat_type is not None:
                result['substatType'] = substat_type
                result['substatValue'] = substat_value
            return result
    except Exception as e:
        pass
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global character_list_cache, weapon_list_cache
    print("正在初始化数据...")
    character_list_cache = fetch_character_list()
    weapon_list_cache = fetch_weapon_list()
    print(f"初始化完成，角色: {len(character_list_cache)}, 武器: {len(weapon_list_cache)}")
    yield

app = FastAPI(lifespan=lifespan)

class SelfPanelData(BaseModel):
    charBaseAtk: float = 0
    selfCritRate: float = 5
    selfCritDmg: float = 150
    charLevel: int = 90

class WeaponPanelData(BaseModel):
    weaponBaseAtk: float = 0
    weaponSubStat: Optional[str] = None
    weaponSubStatValue: float = 0

class EchoPanelData(BaseModel):
    echoAtkPercent: float = 86
    echoAtkFlat: float = 0
    echoElemDmg: float = 60
    echoNormalDmg: float = 0
    echoHeavyDmg: float = 0
    echoResonanceDmg: float = 0
    echoLiberationDmg: float = 0
    echoCritRate: float = 37.5
    echoCritDmg: float = 92
    cost4MainStat: Optional[str] = None

class CharacterData(BaseModel):
    selfPanel: SelfPanelData
    weaponPanel: WeaponPanelData
    echoPanel: EchoPanelData

class EnemyData(BaseModel):
    enemyLevel: int = 100
    elemResist: float = 10

class BuffData(BaseModel):
    mulBoost: float = 0
    mulDeepen: float = 0
    buffAtkPercent: float = 0
    buffElemDmg: float = 0
    buffNormalDmg: float = 0
    buffHeavyDmg: float = 0
    buffResonanceDmg: float = 0
    buffLiberationDmg: float = 0
    buffCritRate: float = 0
    buffCritDmg: float = 0

class Skill(BaseModel):
    id: int
    name: str
    multiplier: float
    type: str
    isEchoSkill: bool

class Rotation(BaseModel):
    skillId: int
    count: int

class CalculationRequest(BaseModel):
    charData: CharacterData
    enemyData: EnemyData
    buffData: BuffData
    skills: List[Skill]
    rotations: List[Rotation]

class SkillResult(BaseModel):
    skill: Skill
    count: int
    singleDamage: int
    totalSkillDamage: int

class CalculationStep(BaseModel):
    title: str
    content: str

class CalculationResponse(BaseModel):
    success: bool
    finalAttack: Optional[int] = None
    totalDamage: Optional[int] = None
    skillResults: Optional[List[SkillResult]] = None
    calculationSteps: Optional[List[CalculationStep]] = None
    error: Optional[str] = None

def calculate_final_attack_with_steps(char_data: CharacterData, buff_data: BuffData):
    self_panel = char_data.selfPanel
    weapon_panel = char_data.weaponPanel
    echo_panel = char_data.echoPanel
    
    steps = []
    
    char_base_atk = self_panel.charBaseAtk
    weapon_base_atk = weapon_panel.weaponBaseAtk
    
    atk_percent = echo_panel.echoAtkPercent + (buff_data.buffAtkPercent or 0)
    atk_flat = echo_panel.echoAtkFlat
    
    if weapon_panel.weaponSubStat == 'atkPercent':
        atk_percent += weapon_panel.weaponSubStatValue
        steps.append(CalculationStep(
            title="武器副属性加成",
            content=f"攻击力百分比 +{weapon_panel.weaponSubStatValue}%"
        ))
    
    final_atk = char_base_atk + weapon_base_atk * (1 + atk_percent / 100) + atk_flat
    
    steps.insert(0, CalculationStep(
        title="最终攻击力计算",
        content=f"角色基础攻击: {char_base_atk} + 武器基础攻击: {weapon_base_atk} × (1 + 攻击%: {atk_percent}%) + 攻击固定值: {atk_flat} = {round(final_atk)}"
    ))
    
    return round(final_atk), steps

def calculate_total_crit_rate(char_data: CharacterData, buff_data: BuffData):
    self_panel = char_data.selfPanel
    weapon_panel = char_data.weaponPanel
    echo_panel = char_data.echoPanel
    
    crit_rate = self_panel.selfCritRate + echo_panel.echoCritRate + (buff_data.buffCritRate or 0)
    
    if weapon_panel.weaponSubStat == 'critRate':
        crit_rate += weapon_panel.weaponSubStatValue
    
    if echo_panel.cost4MainStat == 'critRate':
        crit_rate += 22
    
    return crit_rate

def calculate_total_crit_dmg(char_data: CharacterData, buff_data: BuffData):
    self_panel = char_data.selfPanel
    weapon_panel = char_data.weaponPanel
    echo_panel = char_data.echoPanel
    
    crit_dmg = self_panel.selfCritDmg + echo_panel.echoCritDmg + (buff_data.buffCritDmg or 0)
    
    if weapon_panel.weaponSubStat == 'critDmg':
        crit_dmg += weapon_panel.weaponSubStatValue
    
    if echo_panel.cost4MainStat == 'critDmg':
        crit_dmg += 44
    
    return crit_dmg

def calculate_skill_damage(skill: Skill, char_data: CharacterData, enemy_data: EnemyData, buff_data: BuffData, steps: List[CalculationStep]):
    final_atk, atk_steps = calculate_final_attack_with_steps(char_data, buff_data)
    steps.extend(atk_steps)
    
    skill_multiplier = skill.multiplier / 100
    mul_boost = 1 + buff_data.mulBoost / 100
    mul_deepen = 1 + buff_data.mulDeepen / 100
    
    self_panel = char_data.selfPanel
    echo_panel = char_data.echoPanel
    
    skill_dmg_bonus = 0
    if skill.type == 'normal':
        skill_dmg_bonus = (echo_panel.echoNormalDmg + (buff_data.buffNormalDmg or 0)) / 100
    elif skill.type == 'heavy':
        skill_dmg_bonus = (echo_panel.echoHeavyDmg + (buff_data.buffHeavyDmg or 0)) / 100
    elif skill.type == 'resonance':
        skill_dmg_bonus = (echo_panel.echoResonanceDmg + (buff_data.buffResonanceDmg or 0)) / 100
    elif skill.type == 'liberation':
        skill_dmg_bonus = (echo_panel.echoLiberationDmg + (buff_data.buffLiberationDmg or 0)) / 100
    
    elem_dmg = (echo_panel.echoElemDmg + (buff_data.buffElemDmg or 0)) / 100
    dmg_bonuses = elem_dmg + skill_dmg_bonus
    total_dmg_bonus = 1 + dmg_bonuses
    
    total_crit_rate = min(calculate_total_crit_rate(char_data, buff_data) / 100, 1)
    total_crit_dmg = calculate_total_crit_dmg(char_data, buff_data) / 100
    crit_expectation = 1 + total_crit_rate * total_crit_dmg
    
    char_level = self_panel.charLevel
    enemy_level = enemy_data.enemyLevel
    level_multiplier = (100 + char_level) / (199 + char_level + enemy_level)
    
    elem_resist = enemy_data.elemResist / 100
    resist_multiplier = 1 - elem_resist
    
    damage = final_atk * skill_multiplier * mul_boost * mul_deepen * \
             total_dmg_bonus * crit_expectation * level_multiplier * resist_multiplier
    
    steps.append(CalculationStep(
        title="技能伤害计算",
        content=f"最终攻击: {final_atk} × 技能倍率: {skill.multiplier}% × 倍率提升: {buff_data.mulBoost}% × 倍率加深: {buff_data.mulDeepen}% × 伤害加成: {(dmg_bonuses*100):.1f}% × 暴击期望: {(crit_expectation*100):.1f}% × 等级倍率: {level_multiplier:.4f} × 抗性倍率: {resist_multiplier:.2f} = {round(damage)}"
    ))
    
    return round(damage)

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/api/characters")
async def get_characters():
    return {"success": True, "characters": character_list_cache}

@app.get("/api/weapons")
async def get_weapons(weapon_type: Optional[str] = None):
    print(f"收到武器列表请求，weapon_type: {weapon_type}")
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
        all_steps = []
        
        for rotation in rotations:
            skill_id = rotation.skillId
            count = rotation.count
            if count > 0:
                skill = next((s for s in skills_list if s.id == skill_id), None)
                if skill:
                    steps = []
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
