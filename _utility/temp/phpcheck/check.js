const fs = require("fs");
const engine = require("php-parser");

const file = process.argv[2];
const code = fs.readFileSync(file, "utf8");

const parser = new engine({
	parser: { suppressErrors: true, extractDoc: false, version: 802 },
	ast: { withPositions: true },
});

const ast = parser.parseCode(code, file);
const errors = ast.errors || [];

if (errors.length) {
	console.log("PARSE: ERRORI (" + errors.length + ")");
	for (const e of errors) {
		console.log(`  riga ${e.line || (e.loc && e.loc.start && e.loc.start.line)}: ${e.message}`);
	}
	process.exit(1);
} else {
	console.log("PARSE: OK — nessun errore di sintassi, file intero validato");
}
