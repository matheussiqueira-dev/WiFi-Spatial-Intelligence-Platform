import fs from "node:fs";
import { chromium, firefox, webkit } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";
const browsers = Object.fromEntries(
  Object.entries({ chromium, firefox, webkit }).map(([name, browser]) => {
    const executable = browser.executablePath();
    return [name, { executable, available: fs.existsSync(executable) }];
  }),
);
const root = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
const packages = Object.fromEntries(
  ["next", "react", "react-dom", "zod", "@playwright/test", "typescript"].map(
    (name) => {
      const metadata = JSON.parse(
        fs.readFileSync(
          path.join(root, "node_modules", name, "package.json"),
          "utf8",
        ),
      );
      return [
        name,
        {
          version: metadata.version,
          license: metadata.license ?? "UNVERIFIED",
        },
      ];
    },
  ),
);
console.log(
  JSON.stringify({ node: process.version, browsers, packages }, null, 2),
);
