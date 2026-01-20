import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/orders/{id}/messages",
  summary: "List order messages",
  description: "Returns paginated messages for an order",
  tags: ["Order Messages"],
  operationId: "listOrderMessages",
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
