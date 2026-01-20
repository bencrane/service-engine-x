import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/orders/{id}/tasks",
  summary: "Create order task",
  description: "Creates a new task on an order",
  tags: ["Order Tasks"],
  operationId: "createOrderTask",
  responses: {
    "201": {
      description: "Task created",
    },
    "400": {
      description: "Validation error",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Order not found",
    },
  },
};
