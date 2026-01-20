import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/orders/{id}/tasks",
  summary: "List order tasks",
  description: "Returns tasks for an order",
  tags: ["Order Tasks"],
  operationId: "listOrderTasks",
  responses: {
    "200": {
      description: "Successful response",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Order not found",
    },
  },
};
