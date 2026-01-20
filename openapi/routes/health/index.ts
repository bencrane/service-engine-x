import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/health",
  summary: "Health check",
  description: "Returns API health status",
  tags: ["System"],
  operationId: "healthCheck",
  responses: {
    "200": {
      description: "API is healthy",
    },
  },
};
