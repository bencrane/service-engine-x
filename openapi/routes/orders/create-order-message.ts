import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/orders/{id}/messages",
  summary: "Create order message",
  description: "Creates a new message on an order",
  tags: ["Order Messages"],
  operationId: "createOrderMessage",
  responses: {
    "201": {
      description: "Message created",
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
