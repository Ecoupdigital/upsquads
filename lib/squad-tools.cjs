#!/usr/bin/env node

/**
 * UPSquads Tools — CLI utility for squad management
 *
 * Usage: node squad-tools.cjs <command> [args] [--raw]
 *
 * Commands:
 *   list                    List all available squads
 *   info <name>             Show squad details
 *   install <name>          Install a squad (copy agents to ~/.claude/agents/)
 *   remove <name>           Remove an installed squad
 *   installed               List installed squads
 */

const fs = require('fs');
const path = require('path');

// --- Output helpers ---
const raw = process.argv.includes('--raw');

function output(data) {
  if (raw) {
    console.log(JSON.stringify(data));
  } else {
    console.log(JSON.stringify(data, null, 2));
  }
  process.exit(0);
}

function error(msg) {
  if (raw) {
    console.log(JSON.stringify({ error: msg }));
  } else {
    console.error(`Error: ${msg}`);
  }
  process.exit(1);
}

// --- Paths ---
function getSquadsDir() {
  // Installed location (~/.claude/upsquads/squads/) takes priority
  const installed = path.join(require('os').homedir(), '.claude', 'upsquads', 'squads');
  if (fs.existsSync(installed)) return installed;
  // Fallback: relative to this script (dev mode)
  const dev = path.join(__dirname, '..', 'squads');
  if (fs.existsSync(dev)) return dev;
  return installed;
}

function getAgentsDir() {
  return path.join(require('os').homedir(), '.claude', 'agents');
}

// --- Registry ---
function loadRegistry() {
  const registryPath = path.join(getSquadsDir(), 'registry.yaml');
  if (!fs.existsSync(registryPath)) error('Squad registry not found. Run: npx upsquads install');
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

function isSquadInstalled(squadId) {
  const markerPath = path.join(getSquadsDir(), squadId, '.installed');
  return fs.existsSync(markerPath);
}

function getSquadAgentFiles(squadId) {
  const agentsDir = path.join(getSquadsDir(), squadId, 'agents');
  if (!fs.existsSync(agentsDir)) return [];
  return fs.readdirSync(agentsDir).filter(f => f.endsWith('.md'));
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

  return `---
name: ${fullName}
description: "${description.replace(/"/g, "'")}"
tools: Read, Write, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion
color: ${color}
---

`;
}

// --- Commands ---
function cmdList() {
  const squads = loadRegistry();
  const result = squads.map(s => ({
    ...s,
    installed: isSquadInstalled(s.id),
  }));
  output({ squads: result });
}

function cmdInfo(squadId) {
  if (!squadId) error('squad name required: squad info <name>');
  const squads = loadRegistry();
  const squad = squads.find(s => s.id === squadId);
  if (!squad) error(`Squad not found: ${squadId}\nAvailable: ${squads.map(s => s.id).join(', ')}`);

  const agentFiles = getSquadAgentFiles(squadId);
  const agents = agentFiles.map(f => f.replace('.md', ''));

  const tasksDir = path.join(getSquadsDir(), squadId, 'tasks');
  const tasks = fs.existsSync(tasksDir)
    ? fs.readdirSync(tasksDir).filter(f => f.endsWith('.md')).map(f => f.replace('.md', ''))
    : [];

  const wfDir = path.join(getSquadsDir(), squadId, 'workflows');
  const workflows = fs.existsSync(wfDir)
    ? fs.readdirSync(wfDir).filter(f => f.endsWith('.yaml') || f.endsWith('.yml')).map(f => f.replace(/\.ya?ml$/, ''))
    : [];

  output({
    ...squad,
    installed: isSquadInstalled(squadId),
    agents,
    tasks,
    workflows,
  });
}

function cmdInstall(squadId) {
  if (!squadId) error('squad name required: squad install <name>');
  const squads = loadRegistry();
  const squad = squads.find(s => s.id === squadId);
  if (!squad) error(`Squad not found: ${squadId}\nAvailable: ${squads.map(s => s.id).join(', ')}`);

  if (isSquadInstalled(squadId)) {
    output({ status: 'already_installed', squad: squadId });
    return;
  }

  const agentsDestDir = getAgentsDir();
  fs.mkdirSync(agentsDestDir, { recursive: true });

  const agentFiles = getSquadAgentFiles(squadId);
  const installed = [];

  for (const file of agentFiles) {
    const srcPath = path.join(getSquadsDir(), squadId, 'agents', file);
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

    const destPath = path.join(agentsDestDir, `${fullName}.md`);
    fs.writeFileSync(destPath, finalContent, 'utf8');
    installed.push(fullName);
  }

  const markerPath = path.join(getSquadsDir(), squadId, '.installed');
  fs.writeFileSync(markerPath, new Date().toISOString(), 'utf8');

  output({ status: 'installed', squad: squadId, agents: installed, count: installed.length });
}

function cmdRemove(squadId) {
  if (!squadId) error('squad name required: squad remove <name>');

  if (!isSquadInstalled(squadId)) {
    output({ status: 'not_installed', squad: squadId });
    return;
  }

  const agentsDir = getAgentsDir();
  const prefix = `sq-${squadId}-`;
  let removed = 0;

  if (fs.existsSync(agentsDir)) {
    for (const file of fs.readdirSync(agentsDir)) {
      if (file.startsWith(prefix) && file.endsWith('.md')) {
        fs.unlinkSync(path.join(agentsDir, file));
        removed++;
      }
    }
  }

  const markerPath = path.join(getSquadsDir(), squadId, '.installed');
  if (fs.existsSync(markerPath)) fs.unlinkSync(markerPath);

  output({ status: 'removed', squad: squadId, agents_removed: removed });
}

function cmdInstalled() {
  const squads = loadRegistry();
  const installed = squads.filter(s => isSquadInstalled(s.id));
  output({ installed: installed.map(s => s.id), count: installed.length });
}

// --- Main ---
function main() {
  const args = process.argv.slice(2).filter(a => a !== '--raw');
  const command = args[0];

  switch (command) {
    case 'list': cmdList(); break;
    case 'info': cmdInfo(args[1]); break;
    case 'install': cmdInstall(args[1]); break;
    case 'remove': cmdRemove(args[1]); break;
    case 'installed': cmdInstalled(); break;
    default:
      error('Usage: squad-tools.cjs list|info|install|remove|installed [<name>]');
  }
}

main();
