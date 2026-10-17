Deno.serve(async (req: Request) => {
  if (req.method !== "GET" && req.method !== "HEAD") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { "Content-Type": "text/plain; charset=utf-8", "Allow": "GET, HEAD" }
    });
  }

  // Do not let a CDN serve a stale workspace after the branch has changed.
  const upstream = await fetch("https://raw.githubusercontent.com/rllibo833-sudo/pusingcuk/warungpusingcuk/web/index.html", {
    headers: { "Accept": "text/html", "Cache-Control": "no-cache" },
    cache: "no-store"
  });

  if (!upstream.ok) {
    return new Response("Frontend source unavailable. HTTP " + upstream.status, {
      status: 502,
      headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }
    });
  }

  const html = await upstream.text();
  const headers = new Headers();
  headers.set("Content-Type", "text/html; charset=utf-8");
  headers.set("Cache-Control", "no-store, max-age=0");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  return new Response(req.method === "HEAD" ? null : html, { status: 200, headers });
});
