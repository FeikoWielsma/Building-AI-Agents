import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new Server(
  {
    name: "time-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

await server.setRequestHandler(
  z.object({
    method: z.literal("tools/call"),
    params: z.object({
      name: z.literal("get-current-time"),
      arguments: z.object({
        format: z
          .enum(["ISO", "DateTime", "UnixTimestamp", "HH:MM:SS"])
          .optional()
          .default("ISO"),
        timezone: z.string().optional().default("local"),
      }),
    }),
  }),
  async ({ name, arguments: { format, timezone } }) => {
    const now = new Date();
    
    let result = {
      timestamp: now.getTime(),
      iso: now.toISOString(),
      dateTime: now.toLocaleString(),
      unix: Math.floor(now.getTime() / 1000),
    };
    
    if (format === "ISO") result.content = [
      { type: "text", text: `ISO: ${result.iso}` }
    ];
    else if (format === "DateTime") result.content = [
      { type: "text", text: `Date/Time: ${result.dateTime}` }
    ];
    else if (format === "UnixTimestamp") result.content = [
      { type: "text", text: `Unix Timestamp: ${result.unix}` }
    ];
    else if (format === "HH:MM:SS") result.content = [
      { type: "text", text: `Time: ${now.toLocaleTimeString()}` }
    ];
    
    result.content.push(
      { type: "text", text: `Full: ${result.iso}` },
      { type: "text", text: `Timezone: ${timezone || "local"}` }
    );
    
    return { content: result.content };
  }
);

server.setRequestHandler(z.object({
  method: z.literal("notifications/initialized")
}), async () => {
  console.log("Time server initialized");
});

if (import.meta.main) {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
