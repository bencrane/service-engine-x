import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "DELETE",
  path: "/api/order-messages/{id}",
  summary: "Delete order message",
  description: "Permanently deletes an order message",
  tags: ["Order Messages"],
  operationId: "deleteOrderMessage",
  responses: {
    "204": {
      description: "Message deleted",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Message not found",
    },
  },
};
