const DEFAULT_API_URL = "https://acervo-api-production.up.railway.app";
const DEFAULT_ALLOWED_HOSTS = "acervo-vasco.vercel.app";

function allowedFrontendRequest(req) {
  const allowedHosts = (process.env.ACERVO_ALLOWED_FRONT_HOSTS || DEFAULT_ALLOWED_HOSTS)
    .split(",")
    .map((host) => host.trim().toLowerCase())
    .filter(Boolean);
  const requestHost = String(req.headers.host || "").split(":")[0].toLowerCase();
  const fetchSite = String(req.headers["sec-fetch-site"] || "").toLowerCase();
  const fetchDest = String(req.headers["sec-fetch-dest"] || "").toLowerCase();
  if (["same-origin", "same-site"].includes(fetchSite) && ["", "script", "empty"].includes(fetchDest)) {
    return true;
  }

  const source = req.headers.origin || req.headers.referer || "";
  if (!source) return false;

  try {
    const sourceHost = new URL(source).host.split(":")[0].toLowerCase();
    return sourceHost === requestHost || allowedHosts.includes(sourceHost);
  } catch {
    return false;
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  if (!allowedFrontendRequest(req)) {
    res.status(403).send("Origem não autorizada.");
    return;
  }

  const token = process.env.ACERVO_DATA_TOKEN;
  if (!token) {
    res.status(500).send("ACERVO_DATA_TOKEN não configurado na Vercel.");
    return;
  }

  const apiUrl = (process.env.ACERVO_API_URL || DEFAULT_API_URL).replace(/\/$/, "");
  const upstream = await fetch(`${apiUrl}/data-runtime.js`, {
    headers: {
      "x-acervo-data-token": token,
    },
  });
  const body = await upstream.text();

  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("Content-Type", upstream.headers.get("content-type") || "application/javascript; charset=utf-8");
  res.status(upstream.status).send(body);
};
