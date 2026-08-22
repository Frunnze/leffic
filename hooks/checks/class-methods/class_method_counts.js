const fs = require("fs");

const MAXIMUM_METHODS = 4;

const typescript = require(process.argv[2]);

function isStatic(member) {
  const modifiers = member.modifiers === undefined ? [] : member.modifiers;

  return modifiers.some(
    (modifier) => modifier.kind === typescript.SyntaxKind.StaticKeyword,
  );
}

function isInstanceMethod(member) {
  const isMethod =
    typescript.isMethodDeclaration(member) ||
    typescript.isConstructorDeclaration(member) ||
    typescript.isGetAccessorDeclaration(member) ||
    typescript.isSetAccessorDeclaration(member);

  return isMethod && !isStatic(member);
}

function methodCountOf(node) {
  return node.members.filter(isInstanceMethod).length;
}

function reportFor(sourceFile, node, methodCount) {
  const start = sourceFile.getLineAndCharacterOfPosition(node.getStart());
  const name = node.name === undefined ? "(anonymous)" : node.name.text;

  const summary = `${name} has ${methodCount} methods`;

  return `${sourceFile.fileName}:${start.line + 1}: ${summary}`;
}

function collectCrowdedFrom(sourceFile, node, found) {
  const isClass =
    typescript.isClassDeclaration(node) || typescript.isClassExpression(node);

  if (isClass && methodCountOf(node) > MAXIMUM_METHODS) {
    found.push(reportFor(sourceFile, node, methodCountOf(node)));
  }

  typescript.forEachChild(node, (child) =>
    collectCrowdedFrom(sourceFile, child, found),
  );
}

function scriptKindOf(filePath) {
  return filePath.endsWith(".tsx")
    ? typescript.ScriptKind.TSX
    : typescript.ScriptKind.TS;
}

function crowdedClassesIn(filePath) {
  const sourceFile = typescript.createSourceFile(
    filePath,
    fs.readFileSync(filePath, "utf8"),
    typescript.ScriptTarget.Latest,
    true,
    scriptKindOf(filePath),
  );
  const found = [];

  collectCrowdedFrom(sourceFile, sourceFile, found);

  return found;
}

const sourcePaths = fs.readFileSync(0, "utf8").split(/\s+/).filter(Boolean);
const reported = [];

for (const filePath of sourcePaths) {
  reported.push(...crowdedClassesIn(filePath));
}

for (const crowded of reported.sort()) process.stdout.write(crowded + "\n");
