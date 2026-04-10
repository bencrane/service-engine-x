export function classifyHttpStatus(status) {
    if (status === 401 || status === 403)
        return "auth_error";
    if (status === 404)
        return "not_found";
    if (status === 409)
        return "conflict";
    if (status >= 400 && status < 500)
        return "validation_error";
    return "upstream_error";
}
export function buildActionableMessage(category, detail, toolName) {
    switch (category) {
        case "auth_error":
            return `${detail} Verify MCP ingress bearer secret and downstream API credentials for ${toolName}.`;
        case "validation_error":
            return `${detail} Validate required fields and re-run ${toolName} with corrected input.`;
        case "not_found":
            return `${detail} Confirm org-scoped identifiers first using a related read tool before retrying ${toolName}.`;
        case "conflict":
            return `${detail} Resource state conflicts with this operation; read current state and apply a valid transition before retry.`;
        default:
            return `${detail} Upstream service failed; retry if transient and inspect upstream status/response.`;
    }
}
//# sourceMappingURL=errors.js.map