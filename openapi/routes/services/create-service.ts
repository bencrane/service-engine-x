import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/services",
  summary: "Create a service",
  description: "Creates a new service",
  tags: ["Services"],
  operationId: "createService",
  responses: {
    "201": {
      description: "Service created",
    },
    "400": {
      description: "Validation error",
    },
    "401": {
      description: "Unauthorized",
    },
  },
};
