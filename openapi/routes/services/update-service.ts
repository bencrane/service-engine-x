import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "PUT",
  path: "/api/services/{id}",
  summary: "Update a service",
  description: "Updates an existing service",
  tags: ["Services"],
  operationId: "updateService",
  responses: {
    "200": {
      description: "Service updated",
    },
    "400": {
      description: "Validation error",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Service not found",
    },
  },
};
