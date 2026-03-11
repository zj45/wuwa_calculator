from pydantic import BaseModel
from typing import List, Optional

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
