let skills = [];
let skillRotations = [];
let characterList = [];
let lastCalculationData = null;

function safeGetElement(id) {
    return document.getElementById(id);
}

function safeSetText(id, text) {
    const el = safeGetElement(id);
    if (el) {
        el.textContent = text;
    }
}

function safeSetHTML(id, html) {
    const el = safeGetElement(id);
    if (el) {
        el.innerHTML = html;
    }
}

const skillTypeNames = {
    normal: '普攻',
    heavy: '重击',
    resonance: '共鸣技能',
    liberation: '共鸣解放'
};

let currentWeaponData = {
    substatType: null,
    substatValue: 0
};

function getFormData() {
    const getValue = (id, defaultValue = 0, isInt = false) => {
        const el = document.getElementById(id);
        if (!el) return defaultValue;
        const val = el.value;
        if (val === '' || val === null || val === undefined) return defaultValue;
        return isInt ? parseInt(val) || defaultValue : parseFloat(val) || defaultValue;
    };
    
    const shouAnRenEl = document.getElementById('shouAnRen');
    const isShouAnRen = shouAnRenEl ? shouAnRenEl.checked : false;
    
    const selfPanel = {
        charBaseAtk: getValue('charBaseAtk', 0),
        selfCritRate: getValue('selfCritRate', 5),
        selfCritDmg: getValue('selfCritDmg', 150),
        charLevel: getValue('charLevel', 90, true)
    };
    
    const weaponPanel = {
        weaponBaseAtk: getValue('weaponBaseAtk', 0),
        weaponSubStat: currentWeaponData.substatType,
        weaponSubStatValue: currentWeaponData.substatValue
    };
    
    const cost4MainStatEl = document.getElementById('cost4MainStat');
    const cost4MainStat = cost4MainStatEl ? cost4MainStatEl.value : '';
    
    let echoAtkPercent = getValue('echoAtkPercent', 86);
    let echoCritRate = getValue('echoCritRate', 37.5);
    let echoCritDmg = getValue('echoCritDmg', 92);
    
    if (isShouAnRen) {
        echoAtkPercent += 25;
        echoCritRate += 12.5;
        echoCritDmg += 25;
    }
    
    const echoPanel = {
        echoAtkPercent: echoAtkPercent,
        echoAtkFlat: getValue('echoAtkFlat', 0),
        echoElemDmg: getValue('echoElemDmg', 60),
        echoNormalDmg: getValue('echoNormalDmg', 0),
        echoHeavyDmg: getValue('echoHeavyDmg', 0),
        echoResonanceDmg: getValue('echoResonanceDmg', 0),
        echoLiberationDmg: getValue('echoLiberationDmg', 0),
        echoCritRate: echoCritRate,
        echoCritDmg: echoCritDmg,
        cost4MainStat: cost4MainStat || null
    };
    
    const charData = {
        selfPanel,
        weaponPanel,
        echoPanel
    };
    
    const enemyData = {
        enemyLevel: parseInt(document.getElementById('enemyLevel').value) || 100,
        elemResist: parseFloat(document.getElementById('elemResist').value) || 10
    };
    
    let mulDeepen = parseFloat(document.getElementById('mulDeepen').value) || 0;
    if (isShouAnRen) {
        mulDeepen += 15;
    }
    
    const buffData = {
        mulBoost: parseFloat(document.getElementById('mulBoost').value) || 0,
        mulDeepen: mulDeepen,
        buffAtkPercent: parseFloat(document.getElementById('buffAtkPercent').value) || 0,
        buffElemDmg: parseFloat(document.getElementById('buffElemDmg').value) || 0,
        buffNormalDmg: parseFloat(document.getElementById('buffNormalDmg').value) || 0,
        buffHeavyDmg: parseFloat(document.getElementById('buffHeavyDmg').value) || 0,
        buffResonanceDmg: parseFloat(document.getElementById('buffResonanceDmg').value) || 0,
        buffLiberationDmg: parseFloat(document.getElementById('buffLiberationDmg').value) || 0,
        buffCritRate: parseFloat(document.getElementById('buffCritRate').value) || 0,
        buffCritDmg: parseFloat(document.getElementById('buffCritDmg').value) || 0
    };
    
    return { charData, enemyData, buffData };
}

function updateSummary() {
    const { charData, buffData } = getFormData();
    const selfPanel = charData.selfPanel;
    const weaponPanel = charData.weaponPanel;
    const echoPanel = charData.echoPanel;
    
    let weaponSubstatIsAtkPercent = false;
    let weaponSubstatIsCritRate = false;
    let weaponSubstatIsCritDmg = false;
    let weaponSubstatValue = 0;
    
    if (weaponPanel.weaponSubStat) {
        const substatStr = String(weaponPanel.weaponSubStat);
        
        if (substatStr.includes('攻击') && !substatStr.includes('伤害')) {
            weaponSubstatIsAtkPercent = true;
            weaponSubstatValue = weaponPanel.weaponSubStatValue || 0;
        } else if ((substatStr.includes('暴击') && !substatStr.includes('伤害')) || substatStr.toLowerCase() === 'critrate') {
            weaponSubstatIsCritRate = true;
            weaponSubstatValue = weaponPanel.weaponSubStatValue || 0;
        } else if ((substatStr.includes('暴击') && substatStr.includes('伤害')) || substatStr.toLowerCase() === 'critdmg') {
            weaponSubstatIsCritDmg = true;
            weaponSubstatValue = weaponPanel.weaponSubStatValue || 0;
        }
    }
    
    let finalAtk = selfPanel.charBaseAtk + weaponPanel.weaponBaseAtk * (1 + (echoPanel.echoAtkPercent + (buffData.buffAtkPercent || 0)) / 100) + echoPanel.echoAtkFlat;
    if (weaponSubstatIsAtkPercent) {
        finalAtk = selfPanel.charBaseAtk + weaponPanel.weaponBaseAtk * (1 + (echoPanel.echoAtkPercent + (buffData.buffAtkPercent || 0) + weaponSubstatValue) / 100) + echoPanel.echoAtkFlat;
    }
    
    let critRate = selfPanel.selfCritRate + echoPanel.echoCritRate + (buffData.buffCritRate || 0);
    if (weaponSubstatIsCritRate) {
        critRate += weaponSubstatValue;
    }
    if (echoPanel.cost4MainStat === 'critRate') {
        critRate += 22;
    }
    
    let critDmg = selfPanel.selfCritDmg + echoPanel.echoCritDmg + (buffData.buffCritDmg || 0);
    if (weaponSubstatIsCritDmg) {
        critDmg += weaponSubstatValue;
    }
    if (echoPanel.cost4MainStat === 'critDmg') {
        critDmg += 44;
    }
    
    const elemDmg = echoPanel.echoElemDmg + (buffData.buffElemDmg || 0);
    
    safeSetText('summaryFinalAtk', Math.round(finalAtk).toLocaleString());
    safeSetText('summaryCritRate', critRate.toFixed(1) + '%');
    safeSetText('summaryCritDmg', critDmg.toFixed(1) + '%');
    safeSetText('summaryElemDmg', elemDmg.toFixed(1) + '%');
}

function updateCost4MainStat() {
    updateSummary();
}

function addSkill() {
    const skillNameEl = safeGetElement('skillName');
    const skillMultiplierEl = safeGetElement('skillMultiplier');
    const skillTypeEl = safeGetElement('skillType');
    const isEchoSkillEl = safeGetElement('isEchoSkill');
    
    const name = skillNameEl ? skillNameEl.value.trim() : '';
    const multiplier = skillMultiplierEl ? (parseFloat(skillMultiplierEl.value) || 100) : 100;
    const type = skillTypeEl ? skillTypeEl.value : 'normal';
    const isEchoSkill = isEchoSkillEl ? isEchoSkillEl.checked : false;
    
    if (!name) {
        alert('请输入技能名称');
        return;
    }
    
    const skill = {
        id: Date.now(),
        name,
        multiplier,
        type,
        isEchoSkill
    };
    
    skills.push(skill);
    renderSkills();
    renderRotationBuilder();
    
    if (skillNameEl) skillNameEl.value = '';
    if (skillMultiplierEl) skillMultiplierEl.value = '100';
    if (isEchoSkillEl) isEchoSkillEl.checked = false;
}

function removeSkill(skillId) {
    skills = skills.filter(s => s.id !== skillId);
    skillRotations = skillRotations.filter(r => r.skillId !== skillId);
    renderSkills();
    renderRotationBuilder();
}

function renderSkills() {
    const skillsList = safeGetElement('skillsList');
    if (!skillsList) return;
    skillsList.innerHTML = '';
    
    skills.forEach(skill => {
        const skillElement = document.createElement('div');
        skillElement.className = 'skill-item';
        skillElement.innerHTML = `
            <h3>${skill.name}</h3>
            <p>倍率: ${skill.multiplier}%</p>
            <p>类型: ${skillTypeNames[skill.type]}</p>
            <p>${skill.isEchoSkill ? '✓ 声骸技能' : '✗ 非声骸技能'}</p>
            <button class="btn btn-remove" onclick="removeSkill(${skill.id})">删除</button>
        `;
        skillsList.appendChild(skillElement);
    });
}

function renderRotationBuilder() {
    const rotationBuilder = safeGetElement('rotationBuilder');
    if (!rotationBuilder) return;
    rotationBuilder.innerHTML = '';
    
    skills.forEach(skill => {
        let rotation = skillRotations.find(r => r.skillId === skill.id);
        if (!rotation) {
            rotation = { skillId: skill.id, count: 0 };
            skillRotations.push(rotation);
        }
        
        const rotationElement = document.createElement('div');
        rotationElement.className = 'rotation-item';
        rotationElement.innerHTML = `
            <strong>${skill.name}</strong>
            <span>(${skillTypeNames[skill.type]})</span>
            <input type="number" min="0" value="${rotation.count}" 
                   onchange="updateRotationCount(${skill.id}, this.value)">
            <span>次</span>
        `;
        rotationBuilder.appendChild(rotationElement);
    });
}

function updateRotationCount(skillId, count) {
    const rotation = skillRotations.find(r => r.skillId === skillId);
    if (rotation) {
        rotation.count = Math.max(0, parseInt(count) || 0);
    }
}

async function loadCharacters() {
    try {
        const response = await fetch('/api/characters');
        const result = await response.json();
        if (result.success) {
            characterList = result.characters.map(char => ({
                ...char,
                id: String(char.id)
            }));
            const select = safeGetElement('characterSelect');
            if (select) {
                characterList.forEach(char => {
                    const option = document.createElement('option');
                    option.value = char.id;
                    option.textContent = char.name || char.id;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('加载角色列表失败:', error);
    }
}

async function loadWeapons(weaponType = null) {
    try {
        let url = '/api/weapons';
        if (weaponType !== null && weaponType !== undefined) {
            const wt = String(weaponType);
            url += `?weapon_type=${encodeURIComponent(wt)}`;
        }
        const response = await fetch(url);
        const result = await response.json();
        if (result.success) {
            const select = safeGetElement('weaponSelect');
            if (select) {
                select.innerHTML = '<option value="">-- 请选择武器 --</option>';
                result.weapons.forEach(weapon => {
                    const option = document.createElement('option');
                    option.value = weapon.id;
                    option.textContent = weapon.name || weapon.id;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('加载武器列表失败:', error);
    }
}

async function onCharacterSelect() {
    const characterSelectEl = safeGetElement('characterSelect');
    const characterId = characterSelectEl ? characterSelectEl.value : null;
    if (!characterId) {
        loadWeapons();
        return;
    }
    
    const character = characterList.find(c => String(c.id) === String(characterId));
    
    let weaponType = null;
    if (character) {
        const wt = character.weaponType;
        
        if (wt !== undefined && wt !== null) {
            if (typeof wt === 'object') {
                weaponType = wt.id || wt.Id || wt.value;
            } else {
                weaponType = wt;
            }
        }
    }
    
    if (weaponType !== null && weaponType !== undefined) {
        loadWeapons(weaponType);
    } else {
        loadWeapons();
    }
    
    try {
        const response = await fetch(`/api/character/${characterId}`);
        const result = await response.json();
        if (result.success && result.data && result.data.baseAtk !== undefined) {
            const el = safeGetElement('charBaseAtk');
            if (el) {
                el.value = result.data.baseAtk;
                updateSummary();
            }
        }
    } catch (error) {
        console.error('获取角色详情失败:', error);
    }
}

async function onWeaponSelect() {
    const weaponSelectEl = safeGetElement('weaponSelect');
    const weaponId = weaponSelectEl ? weaponSelectEl.value : null;
    
    currentWeaponData = { substatType: null, substatValue: 0 };
    const substatEl = safeGetElement('weaponSubStat');
    if (substatEl) substatEl.value = '';
    
    if (!weaponId) {
        updateSummary();
        return;
    }
    
    try {
        const response = await fetch(`/api/weapon/${weaponId}`);
        const result = await response.json();
        if (result.success && result.data) {
            if (result.data.baseAtk !== undefined) {
                const el = safeGetElement('weaponBaseAtk');
                if (el) {
                    el.value = result.data.baseAtk;
                }
            }
            
            if (result.data.substatType && result.data.substatType !== null) {
                currentWeaponData.substatType = result.data.substatType;
                currentWeaponData.substatValue = result.data.substatValue || 0;
                
                const substatEl = safeGetElement('weaponSubStat');
                if (substatEl) {
                    const substatName = result.data.substatType;
                    const value = currentWeaponData.substatValue;
                    if (substatName && value !== undefined && value !== null) {
                        substatEl.value = `${substatName} +${value}%`;
                    }
                }
            }
            
            updateSummary();
        }
    } catch (error) {
        console.error('获取武器详情失败:', error);
    }
}

async function calculateDamage() {
    if (skills.length === 0) {
        alert('请先添加技能');
        return;
    }
    
    const { charData, enemyData, buffData } = getFormData();
    
    const requestData = {
        charData,
        enemyData,
        buffData,
        skills,
        rotations: skillRotations
    };
    
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            lastCalculationData = {
                charData,
                enemyData,
                buffData,
                finalAttack: result.finalAttack,
                totalDamage: result.totalDamage,
                skillResults: result.skillResults,
                calculationSteps: result.calculationSteps
            };
            renderResults(result.finalAttack, result.totalDamage, result.skillResults, result.calculationSteps);
        } else {
            alert('计算失败: ' + result.error);
        }
    } catch (error) {
        console.error('计算失败:', error);
        alert('请求失败，请确保后端服务已启动: ' + (error.message || error));
    }
}

function renderResults(finalAttack, totalDamage, skillResults, calculationSteps) {
    const resultPanel = safeGetElement('resultPanel');
    if (!resultPanel) return;
    resultPanel.style.display = 'block';
    
    safeSetText('finalAttackDisplay', Math.round(finalAttack).toLocaleString());
    safeSetText('totalDamageDisplay', totalDamage.toLocaleString());
    
    const skillBreakdown = safeGetElement('skillBreakdown');
    if (skillBreakdown) {
        skillBreakdown.innerHTML = '<h3>技能伤害明细</h3>';
        
        skillResults.forEach(result => {
            const breakdownItem = document.createElement('div');
            breakdownItem.className = 'breakdown-item';
            breakdownItem.innerHTML = `
                <span>${result.skill.name} × ${result.count}次</span>
                <span class="damage-value">
                    单次: ${result.singleDamage.toLocaleString()} | 
                    总计: ${result.totalSkillDamage.toLocaleString()}
                </span>
            `;
            skillBreakdown.appendChild(breakdownItem);
        });
    }
    
    if (calculationSteps && calculationSteps.length > 0) {
        const detailContent = safeGetElement('calculationDetailContent');
        if (detailContent) {
            detailContent.innerHTML = '';
            calculationSteps.forEach((step, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'calculation-step';
                stepElement.innerHTML = `
                    <h4>步骤 ${index + 1}: ${step.title}</h4>
                    <p>${step.content}</p>
                `;
                detailContent.appendChild(stepElement);
            });
        }
    }
    
    resultPanel.scrollIntoView({ behavior: 'smooth' });
}

function toggleCalculationDetail() {
    const detail = safeGetElement('calculationDetail');
    const toggleText = safeGetElement('detailToggleText');
    
    if (detail && toggleText) {
        if (detail.style.display === 'none') {
            detail.style.display = 'block';
            toggleText.textContent = '收起计算过程';
        } else {
            detail.style.display = 'none';
            toggleText.textContent = '展开计算过程';
        }
    }
}

function exportToCSV() {
    if (!lastCalculationData) {
        alert('请先计算伤害后再导出');
        return;
    }
    
    const { charData, enemyData, buffData, finalAttack, totalDamage, skillResults } = lastCalculationData;
    
    let csvContent = '';
    
    csvContent += '=== 自身面板 ===\n';
    csvContent += '项目,数值\n';
    csvContent += `角色基础攻击力,${charData.selfPanel.charBaseAtk}\n`;
    csvContent += `自带暴击率 (%),${charData.selfPanel.selfCritRate}\n`;
    csvContent += `自带暴击伤害 (%),${charData.selfPanel.selfCritDmg}\n`;
    csvContent += `角色等级,${charData.selfPanel.charLevel}\n`;
    csvContent += '\n';
    
    csvContent += '=== 武器面板 ===\n';
    csvContent += '项目,数值\n';
    csvContent += `武器基础攻击力,${charData.weaponPanel.weaponBaseAtk}\n`;
    csvContent += `武器副属性,${charData.weaponPanel.weaponSubStat || '无'}\n`;
    if (charData.weaponPanel.weaponSubStat) {
        csvContent += `副属性数值,${charData.weaponPanel.weaponSubStatValue}\n`;
    }
    csvContent += '\n';
    
    csvContent += '=== 声骸面板 ===\n';
    csvContent += '项目,数值\n';
    csvContent += `攻击力百分比加成 (%),${charData.echoPanel.echoAtkPercent}\n`;
    csvContent += `攻击力固定数值加成,${charData.echoPanel.echoAtkFlat}\n`;
    csvContent += `属性伤害加成 (%),${charData.echoPanel.echoElemDmg}\n`;
    csvContent += `普攻伤害加成 (%),${charData.echoPanel.echoNormalDmg}\n`;
    csvContent += `重击伤害加成 (%),${charData.echoPanel.echoHeavyDmg}\n`;
    csvContent += `共鸣技能伤害加成 (%),${charData.echoPanel.echoResonanceDmg}\n`;
    csvContent += `共鸣解放伤害加成 (%),${charData.echoPanel.echoLiberationDmg}\n`;
    csvContent += `暴击率 (%),${charData.echoPanel.echoCritRate}\n`;
    csvContent += `暴击伤害 (%),${charData.echoPanel.echoCritDmg}\n`;
    csvContent += `Cost4主属性,${charData.echoPanel.cost4MainStat || '无'}\n`;
    csvContent += '\n';
    
    csvContent += '=== 敌人面板 ===\n';
    csvContent += '项目,数值\n';
    csvContent += `敌人等级,${enemyData.enemyLevel}\n`;
    csvContent += `属性抗性 (%),${enemyData.elemResist}\n`;
    csvContent += '\n';
    
    csvContent += '=== 场地Buff ===\n';
    csvContent += '项目,数值\n';
    csvContent += `倍率提升 (%),${buffData.mulBoost}\n`;
    csvContent += `倍率加深 (%),${buffData.mulDeepen}\n`;
    csvContent += '\n';
    
    csvContent += '=== 技能列表 ===\n';
    csvContent += '技能名称,倍率 (%),伤害类型,是否声骸技能\n';
    skills.forEach(skill => {
        csvContent += `${skill.name},${skill.multiplier},${skillTypeNames[skill.type]},${skill.isEchoSkill ? '是' : '否'}\n`;
    });
    csvContent += '\n';
    
    csvContent += '=== 计算结果 ===\n';
    csvContent += '最终攻击力,' + Math.round(finalAttack) + '\n';
    csvContent += '总伤害,' + totalDamage + '\n';
    csvContent += '\n';
    
    csvContent += '=== 技能伤害明细 ===\n';
    csvContent += '技能名称,释放次数,单次伤害,总伤害\n';
    skillResults.forEach(result => {
        csvContent += `${result.skill.name},${result.count},${result.singleDamage},${result.totalSkillDamage}\n`;
    });
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    link.setAttribute('href', url);
    link.setAttribute('download', `鸣潮伤害计算_${timestamp}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

document.addEventListener('DOMContentLoaded', () => {
    renderSkills();
    renderRotationBuilder();
    loadCharacters();
    loadWeapons();
    
    setTimeout(() => {
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', updateSummary);
            input.addEventListener('input', updateSummary);
        });
        
        updateSummary();
    }, 100);
});
