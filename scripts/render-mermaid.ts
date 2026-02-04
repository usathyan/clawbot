// scripts/render-mermaid.ts
import { readFileSync, writeFileSync } from "node:fs";
import { renderMermaid } from "beautiful-mermaid";

function extractSection(readme: string, heading: string): string {
  const lines = readme.split("\n");
  const startIndex = lines.findIndex(l => l.trim().startsWith(`## ${heading}`));
  if (startIndex === -1) {
    throw new Error(`Section "${heading}" not found in README.md`);
  }
  const rest = lines.slice(startIndex + 1);
  const endIndex = rest.findIndex(l => l.startsWith("## "));
  const sectionLines = endIndex === -1 ? rest : rest.slice(0, endIndex);
  return sectionLines.join("\n");
}

function extractMermaidCode(section: string): string {
  const mermaidBlockRegex = /```mermaid\s*([\s\S]*?)```/i;
  const match = section.match(mermaidBlockRegex);
  if (!match) {
    throw new Error("No ```mermaid``` code block found in section");
  }
  // match[1] is the inner diagram text (without fences)
  return match[1].trim();
}

async function main() {
  const readme = readFileSync("README.md", "utf8");
  const section = extractSection(readme, "How It Works");

  const mermaidCode = extractMermaidCode(section); // e.g. "graph TD\n  A-->B"

  const svg = await renderMermaid(mermaidCode, {
    bg: "#0f0f0f",
    fg: "#e0e0e0",
  });

  writeFileSync("how-it-works.svg", svg, "utf8");
  console.log("Wrote how-it-works.svg");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

