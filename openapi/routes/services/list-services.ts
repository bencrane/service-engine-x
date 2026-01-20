import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/services",
  summary: "List all services",
  description: "Returns a paginated list of services",
  tags: ["Services"],
  operationId: "listServices",
  responses: {
    "200": {
      description: "Successful response",
    },
    "401": {
      description: "Unauthorized",
    },
  },
};
