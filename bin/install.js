#!/usr/bin/env node

/**
 * UPSquads Installer with Interactive Onboarding
 *
 * Usage:
 *   npx upsquads                  # Install with interactive onboarding
 *   npx upsquads --all            # Install all squads (skip onboarding)
 *   npx upsquads --uninstall      # Remove from ~/.claude/
 *   node bin/install.js            # Dev install
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// --- Colors ---
const green = '\x1b[32m';
const cyan = '\x1b[36m';
const yellow = '\x1b[33m';
const red = '\x1b[31m';
const dim = '\x1b[2m';
const bold = '\x1b[1m';
const reset = '\x1b[0m';

const packageRoot = path.resolve(__dirname, '..');
const claudeDir = path.join(require('os').homedir(), '.claude');
const upsquadsDir = path.join(claudeDir, 'upsquads');

// --- Helpers ---
function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  let count = 0;
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (entry.name.startsWith('.') && entry.name !== '.gitkeep') continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      count += copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
      count++;
    }
  }
  return count;
}

function loadRegistryFromSource() {
  const registryPath = path.join(packageRoot, 'squads', 'registry.yaml');
  if (!fs.existsSync(registryPath)) return [];
  const content = fs.readFileSync(registryPath, 'utf8');
  const squads = [];
  let current = null;
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- id:')) {
      if (current) squads.push(current);
      current = { id: trimmed.replace('- id:', '').trim() };
    } else if (current && trimmed.startsWith('name:')) {
      current.name = trimmed.replace('name:', '').trim().replace(/^["']|["']$/g, '');
    } else if (current && trimmed.startsWith('agents:')) {
      current.agents = parseInt(trimmed.replace('agents:', '').trim(), 10);
    } else if (current && trimmed.startsWith('description:')) {
      current.description = trimmed.replace('description:', '').trim().replace(/^["']|["']$/g, '');
    } else if (current && trimmed.startsWith('tags:')) {
      const tagsStr = trimmed.replace('tags:', '').trim();
      current.tags = tagsStr.replace(/[\[\]]/g, '').split(',').map(s => s.trim()).filter(Boolean);
    } else if (current && trimmed.startsWith('dominio:')) {
      current.dominio = trimmed.replace('dominio:', '').trim().replace(/^["']|["']$/g, '');
    }
  }
  if (current) squads.push(current);
  return squads;
}

function extractAgentDescription(content) {
  const match = content.match(/>\s*ACTIVATION-NOTICE:\s*(.+)/);
  if (match) return match[1].trim().slice(0, 120);
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && !trimmed.startsWith('```') && !trimmed.startsWith('>') && !trimmed.startsWith('---')) {
      return trimmed.slice(0, 120);
    }
  }
  return 'Squad agent';
}

function buildFrontmatter(squadId, agentFilename, content) {
  const agentName = agentFilename.replace('.md', '');
  const fullName = `sq-${squadId}-${agentName}`;
  const description = extractAgentDescription(content);
  const isChief = agentName.includes('chief') || agentName.includes('chair') || agentName.includes('orchestr');
  const color = isChief ? 'blue' : 'yellow';
  return `---\nname: ${fullName}\ndescription: "${description.replace(/"/g, "'")}"\ntools: Read, Write, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion\ncolor: ${color}\n---\n\n`;
}

function installSquadAgents(squadId) {
  const agentsDir = path.join(upsquadsDir, 'squads', squadId, 'agents');
  if (!fs.existsSync(agentsDir)) return 0;

  const agentsDest = path.join(claudeDir, 'agents');
  fs.mkdirSync(agentsDest, { recursive: true });

  const files = fs.readdirSync(agentsDir).filter(f => f.endsWith('.md'));
  for (const file of files) {
    const srcPath = path.join(agentsDir, file);
    const content = fs.readFileSync(srcPath, 'utf8');
    const agentName = file.replace('.md', '');
    const fullName = `sq-${squadId}-${agentName}`;

    const hasFrontmatter = content.trimStart().startsWith('---');
    let finalContent;
    if (hasFrontmatter) {
      const bodyMatch = content.match(/^---[\s\S]+?---\s*([\s\S]*)$/);
      const body = bodyMatch ? bodyMatch[1] : content;
      finalContent = buildFrontmatter(squadId, file, content) + body;
    } else {
      finalContent = buildFrontmatter(squadId, file, content) + content;
    }

    fs.writeFileSync(path.join(agentsDest, `${fullName}.md`), finalContent, 'utf8');
  }

  // Write .installed marker
  const markerPath = path.join(upsquadsDir, 'squads', squadId, '.installed');
  fs.writeFileSync(markerPath, new Date().toISOString(), 'utf8');

  return files.length;
}

function getSquadAgentNames(squadId) {
  const agentsDir = path.join(packageRoot, 'squads', squadId, 'agents');
  if (!fs.existsSync(agentsDir)) return [];
  return fs.readdirSync(agentsDir)
    .filter(f => f.endsWith('.md'))
    .map(f => f.replace('.md', ''));
}

function ask(rl, question) {
  return new Promise(resolve => rl.question(question, resolve));
}

// --- Banner ---
function showBanner() {
  console.log('');
  console.log(`${cyan}  ╔═╗╔═╗ ╦ ╦╔═╗╔╦╗╔═╗`);
  console.log(`  ╚═╗║═╬╗║ ║╠═╣ ║║╚═╗`);
  console.log(`  ╚═╝╚═╝╚╚═╝╩ ╩═╩╝╚═╝${reset}`);
  console.log('');
  console.log(`  ${cyan}UPSquads${reset} ${dim}v${require('../package.json').version}${reset}`);
  console.log(`  AI agent squads for Claude Code`);
  console.log('');
}

// --- Install base (squads data, lib, command, workflow, orquestrador) ---
function installBase() {
  // 1. Copy squads data
  const squadsSrc = path.join(packageRoot, 'squads');
  const squadsDest = path.join(upsquadsDir, 'squads');
  copyDirRecursive(squadsSrc, squadsDest);

  // 2. Copy lib
  const libSrc = path.join(packageRoot, 'lib');
  const libDest = path.join(upsquadsDir, 'lib');
  copyDirRecursive(libSrc, libDest);

  // 3. Copy orquestrador agent
  const agentsSrc = path.join(packageRoot, 'agents');
  const agentsDest = path.join(claudeDir, 'agents');
  fs.mkdirSync(agentsDest, { recursive: true });
  for (const file of fs.readdirSync(agentsDest)) {
    if (file.startsWith('upsquads-') && file.endsWith('.md')) {
      fs.unlinkSync(path.join(agentsDest, file));
    }
  }
  for (const file of fs.readdirSync(agentsSrc)) {
    if (file.endsWith('.md')) {
      fs.copyFileSync(path.join(agentsSrc, file), path.join(agentsDest, file));
    }
  }

  // 4. Copy /upsq command
  const cmdsSrc = path.join(packageRoot, 'commands');
  const cmdsDest = path.join(claudeDir, 'commands');
  fs.mkdirSync(cmdsDest, { recursive: true });
  for (const file of fs.readdirSync(cmdsSrc)) {
    if (file.endsWith('.md')) {
      fs.copyFileSync(path.join(cmdsSrc, file), path.join(cmdsDest, file));
    }
  }

  // 5. Copy skills to ~/.claude/skills/ (shared capabilities)
  const skillsSrc = path.join(packageRoot, 'skills');
  if (fs.existsSync(skillsSrc)) {
    const skillsDest = path.join(claudeDir, 'skills');
    copyDirRecursive(skillsSrc, skillsDest);
  }

  // 6. Copy workflows
  const wfSrc = path.join(packageRoot, 'workflows');
  const wfDest = path.join(upsquadsDir, 'workflows');
  fs.mkdirSync(wfDest, { recursive: true });
  for (const file of fs.readdirSync(wfSrc)) {
    if (file.endsWith('.md')) {
      fs.copyFileSync(path.join(wfSrc, file), path.join(wfDest, file));
    }
  }

  // 6. Version
  fs.writeFileSync(path.join(upsquadsDir, 'VERSION'), require('../package.json').version, 'utf8');
}

// --- Interactive onboarding ---
async function onboarding() {
  showBanner();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log(`  ${bold}Bem-vindo ao UPSquads!${reset}`);
  console.log(`  Vamos configurar suas squads de agentes AI.`);
  console.log('');
  console.log(`  ${dim}Cada squad e um time de agentes especialistas.${reset}`);
  console.log(`  ${dim}Escolha as que fazem sentido para voce agora.${reset}`);
  console.log(`  ${dim}Voce pode instalar/remover depois com /upsq.${reset}`);
  console.log('');

  // Install base files first
  console.log(`  ${dim}Preparando arquivos base...${reset}`);
  installBase();
  console.log(`  ${green}✓${reset} Base instalada`);
  console.log('');

  const squads = loadRegistryFromSource();
  const selected = [];

  console.log(`  ${bold}${cyan}═══ Squads Disponiveis (${squads.length}) ═══${reset}`);
  console.log('');

  for (let i = 0; i < squads.length; i++) {
    const s = squads[i];
    const agents = getSquadAgentNames(s.id);
    const chiefAgent = agents.find(a => a.includes('chief') || a.includes('chair'));

    // Squad header
    console.log(`  ${bold}${cyan}${i + 1}.${reset} ${bold}${s.name}${reset} ${dim}(${s.agents} agentes)${reset}`);
    console.log(`     ${s.description}`);

    // Show agent names
    if (agents.length > 0) {
      const displayAgents = agents.slice(0, 6).map(a => {
        const isChief = a.includes('chief') || a.includes('chair');
        return isChief ? `${yellow}${a}${reset} ${dim}(chief)${reset}` : dim + a + reset;
      });
      const suffix = agents.length > 6 ? ` ${dim}+${agents.length - 6} mais${reset}` : '';
      console.log(`     ${dim}Agentes:${reset} ${displayAgents.join(', ')}${suffix}`);
    }

    // Tags
    if (s.tags && s.tags.length > 0) {
      console.log(`     ${dim}Tags: ${s.tags.join(', ')}${reset}`);
    }

    console.log('');

    const answer = await ask(rl, `     ${green}Instalar?${reset} [${bold}s${reset}/n/q] `);
    const normalized = answer.trim().toLowerCase();

    if (normalized === 'q') {
      console.log('');
      console.log(`  ${dim}Pulando demais squads...${reset}`);
      break;
    }

    if (normalized === '' || normalized === 's' || normalized === 'y' || normalized === 'sim' || normalized === 'yes') {
      const count = installSquadAgents(s.id);
      selected.push({ ...s, agentCount: count });
      console.log(`     ${green}✓${reset} ${s.name} instalada (${count} agentes)`);
    } else {
      console.log(`     ${dim}— Pulada${reset}`);
    }
    console.log('');
  }

  rl.close();

  // Summary
  console.log('');
  console.log(`  ${bold}${cyan}═══ Resumo ═══${reset}`);
  console.log('');

  if (selected.length === 0) {
    console.log(`  Nenhuma squad instalada. Sem problemas!`);
    console.log(`  Use ${cyan}/upsq listar${reset} a qualquer momento para ver e instalar.`);
  } else {
    const totalAgents = selected.reduce((sum, s) => sum + s.agentCount, 0);
    console.log(`  ${green}✓${reset} ${bold}${selected.length} squad${selected.length > 1 ? 's' : ''}${reset} instalada${selected.length > 1 ? 's' : ''} (${totalAgents} agentes no total)`);
    console.log('');
    for (const s of selected) {
      console.log(`    ${green}•${reset} ${s.name} ${dim}(${s.agentCount} agentes)${reset}`);
    }
  }

  console.log('');
  console.log(`  ${bold}Como usar:${reset}`);
  console.log(`    ${cyan}/upsq${reset}                    Orquestrador interativo`);
  console.log(`    ${cyan}/upsq listar${reset}             Ver todas as squads`);
  console.log(`    ${cyan}/upsq instalar <nome>${reset}    Instalar mais squads`);
  console.log(`    ${cyan}/upsq remover <nome>${reset}     Remover uma squad`);
  console.log(`    ${cyan}/upsq <nome> <task>${reset}      Executar uma task`);
  console.log('');
  console.log(`  ${green}Pronto!${reset} Abra o Claude Code e digite ${cyan}/upsq${reset}`);
  console.log('');
}

// --- Install all (non-interactive) ---
function installAll() {
  showBanner();
  console.log(`  Installing ${bold}all squads${reset} to ${cyan}~/.claude/${reset}`);
  console.log('');

  installBase();
  console.log(`  ${green}✓${reset} Base instalada`);

  const squads = loadRegistryFromSource();
  let totalAgents = 0;

  for (const s of squads) {
    const count = installSquadAgents(s.id);
    totalAgents += count;
    console.log(`  ${green}✓${reset} ${s.name} (${count} agentes)`);
  }

  console.log('');
  console.log(`  ${green}Done!${reset} ${squads.length} squads, ${totalAgents} agentes instalados.`);
  console.log(`  Use ${cyan}/upsq${reset} no Claude Code para comecar.`);
  console.log('');
}

// --- Uninstall ---
function uninstall() {
  console.log('');
  console.log(`  Uninstalling UPSquads from ${cyan}~/.claude/${reset}`);
  console.log('');

  const agentsDir = path.join(claudeDir, 'agents');
  let agentsRemoved = 0;
  if (fs.existsSync(agentsDir)) {
    for (const file of fs.readdirSync(agentsDir)) {
      if ((file.startsWith('sq-') || file.startsWith('upsquads-')) && file.endsWith('.md')) {
        fs.unlinkSync(path.join(agentsDir, file));
        agentsRemoved++;
      }
    }
  }
  if (agentsRemoved > 0) {
    console.log(`  ${green}✓${reset} Removed ${agentsRemoved} squad agents`);
  }

  const cmdFile = path.join(claudeDir, 'commands', 'upsq.md');
  if (fs.existsSync(cmdFile)) {
    fs.unlinkSync(cmdFile);
    console.log(`  ${green}✓${reset} Removed /upsq command`);
  }

  if (fs.existsSync(upsquadsDir)) {
    fs.rmSync(upsquadsDir, { recursive: true });
    console.log(`  ${green}✓${reset} Removed upsquads data`);
  }

  console.log('');
  console.log(`  ${green}Done!${reset} UPSquads fully removed.`);
  console.log('');
}

// --- Main ---
const args = process.argv.slice(2);
if (args.includes('--uninstall') || args.includes('uninstall')) {
  uninstall();
} else if (args.includes('--all') || args.includes('--yes') || args.includes('-y')) {
  installAll();
} else {
  onboarding().catch(err => {
    console.error(`${red}Error:${reset} ${err.message}`);
    process.exit(1);
  });
}
