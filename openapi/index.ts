/**
 * OpenAPI 3.1 Registry
 *
 * Mutable OpenAPI spec that route metadata gets merged into.
 * This is descriptive only - does not affect runtime behavior.
 */

export interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  servers: Array<{
    url: string;
    description?: string;
  }>;
  security: Array<Record<string, string[]>>;
  components: {
    securitySchemes: Record<string, {
      type: string;
      scheme?: string;
      bearerFormat?: string;
      description?: string;
    }>;
    schemas: Record<string, object>;
  };
  paths: Record<string, Record<string, object>>;
}

export const openapi: OpenAPISpec = {
  openapi: "3.1.0",
  info: {
    title: "ServiceEngineX API",
    version: "1.0.0",
    description: "API for ServiceEngineX platform",
  },
  servers: [
    {
      url: "https://api.serviceengine.xyz",
      description: "Production API",
    },
  ],
  security: [
    {
      BearerAuth: [],
    },
  ],
  components: {
    securitySchemes: {
      BearerAuth: {
        type: "http",
        scheme: "bearer",
        bearerFormat: "JWT",
        description: "Bearer token authentication",
      },
    },
    schemas: {},
  },
  paths: {},
};

/**
 * Register a route's OpenAPI metadata into the spec
 */
export function registerRoute(metadata: RouteMetadata): void {
  const { method, path, ...operation } = metadata;
  const methodLower = method.toLowerCase();

  if (!openapi.paths[path]) {
    openapi.paths[path] = {};
  }

  openapi.paths[path][methodLower] = operation;
}

/**
 * Route metadata type for OpenAPI registration
 */
export interface RouteMetadata {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: string;
  summary: string;
  description?: string;
  tags?: string[];
  operationId?: string;
  parameters?: Array<{
    name: string;
    in: "query" | "path" | "header";
    required?: boolean;
    description?: string;
    schema: object;
  }>;
  requestBody?: {
    required?: boolean;
    description?: string;
    content: {
      "application/json": {
        schema: object;
      };
    };
  };
  responses: Record<string, {
    description: string;
    content?: {
      "application/json": {
        schema: object;
      };
    };
  }>;
}

/**
 * Get the assembled OpenAPI spec
 */
export function getOpenAPISpec(): OpenAPISpec {
  return openapi;
}

/**
 * Endpoint summary for API index
 */
export interface EndpointSummary {
  method: string;
  path: string;
  description: string;
}

/**
 * Get a list of all registered endpoints (for /api index)
 * Derived from the OpenAPI registry - not hardcoded
 */
export function getEndpointList(): EndpointSummary[] {
  const endpoints: EndpointSummary[] = [];

  for (const [path, methods] of Object.entries(openapi.paths)) {
    for (const [method, operation] of Object.entries(methods)) {
      const op = operation as { summary?: string; description?: string };
      endpoints.push({
        method: method.toUpperCase(),
        path,
        description: op.summary || op.description || "",
      });
    }
  }

  // Sort by path, then by method
  endpoints.sort((a, b) => {
    const pathCompare = a.path.localeCompare(b.path);
    if (pathCompare !== 0) return pathCompare;
    return a.method.localeCompare(b.method);
  });

  return endpoints;
}
