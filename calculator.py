from models import (
    CharacterData, EnemyData, BuffData, Skill, CalculationStep
)
from typing import List, Tuple


def calculate_final_attack_with_steps(char_data: CharacterData, buff_data: BuffData) -> Tuple[int, List[CalculationStep]]:
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


def calculate_total_crit_rate(char_data: CharacterData, buff_data: BuffData) -> float:
    self_panel = char_data.selfPanel
    weapon_panel = char_data.weaponPanel
    echo_panel = char_data.echoPanel
    
    crit_rate = self_panel.selfCritRate + echo_panel.echoCritRate + (buff_data.buffCritRate or 0)
    
    if weapon_panel.weaponSubStat == 'critRate':
        crit_rate += weapon_panel.weaponSubStatValue
    
    if echo_panel.cost4MainStat == 'critRate':
        crit_rate += 22
    
    return crit_rate


def calculate_total_crit_dmg(char_data: CharacterData, buff_data: BuffData) -> float:
    self_panel = char_data.selfPanel
    weapon_panel = char_data.weaponPanel
    echo_panel = char_data.echoPanel
    
    crit_dmg = self_panel.selfCritDmg + echo_panel.echoCritDmg + (buff_data.buffCritDmg or 0)
    
    if weapon_panel.weaponSubStat == 'critDmg':
        crit_dmg += weapon_panel.weaponSubStatValue
    
    if echo_panel.cost4MainStat == 'critDmg':
        crit_dmg += 44
    
    return crit_dmg


def calculate_skill_damage(
    skill: Skill, 
    char_data: CharacterData, 
    enemy_data: EnemyData, 
    buff_data: BuffData, 
    steps: List[CalculationStep]
) -> int:
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
