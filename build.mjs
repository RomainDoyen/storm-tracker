import config from "./neon.ts";

if (config === null || typeof config !== "object") {
  console.error("neon.ts n'a pas exporté de configuration");
  process.exit(1);
}

console.log("build ok");
