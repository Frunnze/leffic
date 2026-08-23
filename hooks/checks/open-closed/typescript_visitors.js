const { literalDomain } = require("./typescript_registries");

function callableMember(typescript, checker, member) {
  if (typescript.isMethodSignature(member)) {
    return member.questionToken === undefined;
  }
  if (!typescript.isPropertySignature(member)) return false;
  if (member.questionToken !== undefined || member.type === undefined) return false;

  return checker.getTypeFromTypeNode(member.type).getCallSignatures().length > 0;
}

function memberName(typescript, member) {
  if (
    member.name !== undefined &&
    (typescript.isIdentifier(member.name) ||
      typescript.isStringLiteral(member.name))
  ) {
    return member.name.text;
  }

  return undefined;
}

function visitorReports(context) {
  const axes = [];
  const visitors = [];

  function visit(sourceFile, node) {
    if (context.typescript.isTypeAliasDeclaration(node)) {
      const domain = literalDomain(
        context.typescript,
        context.checker.getTypeFromTypeNode(node.type),
      );

      if (domain !== undefined && domain.size >= 3) {
        axes.push({ name: node.name.text, domain });
      }
    }

    const visitorDeclaration =
      context.typescript.isInterfaceDeclaration(node) ||
      (context.typescript.isTypeAliasDeclaration(node) &&
        context.typescript.isTypeLiteralNode(node.type));

    if (visitorDeclaration) {
      const members = context.typescript.isInterfaceDeclaration(node)
        ? node.members
        : node.type.members;

      if (
        members.length >= 3 &&
        members.every((member) =>
          callableMember(
            context.typescript,
            context.checker,
            member,
          ),
        )
      ) {
        const names = members.map((member) =>
          memberName(context.typescript, member),
        );

        if (names.every((name) => name !== undefined)) {
          visitors.push({
            name: node.name.text,
            domain: new Set(names),
            sourceFile,
            position: node.getStart(sourceFile),
          });
        }
      }
    }

    context.typescript.forEachChild(node, (child) => visit(sourceFile, child));
  }

  for (const sourceFile of context.sourceFiles) visit(sourceFile, sourceFile);

  const reports = [];

  for (const visitor of visitors) {
    const key = [...visitor.domain].sort().join("\u0000");
    const axis = axes.find(
      (candidate) => [...candidate.domain].sort().join("\u0000") === key,
    );

    if (axis === undefined) continue;

    const start = visitor.sourceFile.getLineAndCharacterOfPosition(
      visitor.position,
    );
    reports.push(
      `${context.displayPathFor(visitor.sourceFile)}:${start.line + 1}: ` +
        `${visitor.name} requires one callback for every ${axis.name} ` +
        `variant: ${[...visitor.domain].sort().join(", ")}`,
    );
  }

  return reports;
}

module.exports = { visitorReports };
