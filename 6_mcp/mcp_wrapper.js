// Proper CustomEvent polyfill for Node 18+
if (typeof global.CustomEvent === "undefined") {
    global.CustomEvent = class CustomEvent extends Event {
      constructor(type, props = {}) {
        super(type, props);
        this.detail = props.detail;
      }
    };
  }
  
  // Start the MCP server
  import("mcp-memory-libsql").catch(err => {
    console.error("Failed to start mcp-memory-libsql:", err);
    process.exit(1);
  });
  