#!/usr/bin/env node

/**
 * Post-install script for arreio
 * Copies skills from the package to the project's .agents/skills directory
 */

const fs = require('fs');
const path = require('path');

// Determine the source and destination paths
const packageDir = path.dirname(__dirname);
const skillsSource = path.join(packageDir, 'skills');
const agentsDir = path.join(process.cwd(), '.agents');
const skillsDestination = path.join(agentsDir, 'skills');

// Function to recursively copy directories
function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const files = fs.readdirSync(src);
  files.forEach(file => {
    const srcFile = path.join(src, file);
    const destFile = path.join(dest, file);
    const stat = fs.statSync(srcFile);

    if (stat.isDirectory()) {
      copyDirectory(srcFile, destFile);
    } else {
      fs.copyFileSync(srcFile, destFile);
    }
  });
}

try {
  // Create .agents directory if it doesn't exist
  if (!fs.existsSync(agentsDir)) {
    fs.mkdirSync(agentsDir, { recursive: true });
  }

  // Copy skills to .agents/skills
  copyDirectory(skillsSource, skillsDestination);
  console.log(`✓ Arreio skills installed to ${skillsDestination}`);
} catch (error) {
  console.error(`✗ Failed to install Arreio skills: ${error.message}`);
  process.exit(1);
}
