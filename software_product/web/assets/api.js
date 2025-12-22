export function createApiClient(apiBase) {
  const base = apiBase ?? "";

  async function request(path, options = {}) {
    const res = await fetch(base + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    const ct = res.headers.get("content-type") || "";
    const data = ct.includes("application/json") ? await res.json() : await res.text();

    if (!res.ok) {
      const msg = (typeof data === "string")
        ? data
        : (data.detail || data.message || JSON.stringify(data));
      throw new Error(msg);
    }
    return data;
  }

  return {
    listModels: () => request("/api/models", { method: "GET" }),
    status: () => request("/api/model/status", { method: "GET" }),
    loadModel: (model) => request("/api/model/load", {
      method: "POST",
      body: JSON.stringify({ model })
    }),
    generate: (req) => request("/api/generate", {
      method: "POST",
      body: JSON.stringify(req)
    }),
  };
}
