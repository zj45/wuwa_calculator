import requests
from typing import List, Dict, Any, Optional, Tuple

character_list_cache: List[Dict[str, Any]] = []
weapon_list_cache: List[Dict[str, Any]] = []


def fetch_character_list() -> List[Dict[str, Any]]:
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


def fetch_weapon_list() -> List[Dict[str, Any]]:
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


def find_base_atk_from_properties(data: Dict[str, Any]) -> Optional[float]:
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


def find_weapon_substat(data: Dict[str, Any]):
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


def fetch_character_detail(character_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f'https://api-v2.encore.moe/api/zh-Hans/character/{character_id}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            base_atk = find_base_atk_from_properties(data)
            result = {'raw': data}
            if base_atk is not None:
                result['baseAtk'] = base_atk
            return result
    except Exception as e:
        print(f"获取角色详情失败: {e}")
    return None


def fetch_weapon_detail(weapon_id: str) -> Optional[Dict[str, Any]]:
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
        print(f"获取武器详情失败: {e}")
    return None
