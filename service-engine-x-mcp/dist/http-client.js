import { env } from "./env.js";
import { buildActionableMessage, classifyHttpStatus } from "./errors.js";
function buildUrl(path, query) {
    const base = env.SERX_INTERNAL_API_BASE_URL.replace(/\/$/, "");
    const url = new URL(`${base}${path}`);
    if (query) {
        for (const [key, value] of Object.entries(query)) {
            if (value === undefined || value === null || value === "")
                continue;
            if (Array.isArray(value)) {
                for (const item of value) {
                    url.searchParams.append(key, String(item));
                }
                continue;
            }
            url.searchParams.set(key, String(value));
        }
    }
    return url.toString();
}
function headersFor(authMode) {
    if (authMode === "internal") {
        return {
            "content-type": "application/json",
            "x-internal-key": env.SERX_INTERNAL_API_KEY,
        };
    }
    return {
        "content-type": "application/json",
        authorization: `Bearer ${env.SERX_SERVICE_API_TOKEN}`,
    };
}
export async function callSerxApi(args) {
    const url = buildUrl(args.path, args.query);
    const headers = headersFor(args.authMode);
    const response = await fetch(url, {
        method: args.method,
        headers,
        body: args.method === "GET" ? undefined : JSON.stringify(args.body ?? {}),
    });
    let payload = null;
    const rawText = await response.text();
    if (rawText) {
        try {
            payload = JSON.parse(rawText);
        }
        catch {
            payload = rawText;
        }
    }
    if (response.ok) {
        return {
            ok: true,
            status: response.status,
            data: payload,
        };
    }
    const category = classifyHttpStatus(response.status);
    const detail = typeof payload === "object" && payload && "detail" in payload
        ? String(payload.detail)
        : `HTTP ${response.status} from upstream`;
    return {
        ok: false,
        status: response.status,
        data: payload,
        error: {
            category,
            retryable: response.status >= 500,
            status: response.status,
            message: buildActionableMessage(category, detail, args.toolName),
        },
    };
}
//# sourceMappingURL=http-client.js.map