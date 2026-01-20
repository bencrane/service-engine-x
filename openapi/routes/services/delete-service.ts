import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "DELETE",
  path: "/api/services/{id}",
  summary: "Delete a service",
  description: "Soft-deletes a service",
  tags: ["Services"],
  operationId: "deleteService",
  responses: {
    "204": {
      description: "Service deleted",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Service not found",
    },
  },
};
