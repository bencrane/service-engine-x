import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "PUT",
  path: "/api/order-tasks/{id}",
  summary: "Update order task",
  description: "Updates an existing order task",
  tags: ["Order Tasks"],
  operationId: "updateOrderTask",
  responses: {
    "200": {
      description: "Task updated",
    },
    "400": {
      description: "Validation error",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Task not found",
    },
  },
};
