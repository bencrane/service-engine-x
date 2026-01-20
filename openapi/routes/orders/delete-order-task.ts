import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "DELETE",
  path: "/api/order-tasks/{id}",
  summary: "Delete order task",
  description: "Permanently deletes an order task",
  tags: ["Order Tasks"],
  operationId: "deleteOrderTask",
  responses: {
    "204": {
      description: "Task deleted",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Task not found",
    },
  },
};
